import os
import sys
import signal
import random
import logging
from instagrapi import Client
import requests
from rich.console import Console
from time import sleep as time_sleep
from datetime import datetime, timedelta
from automate_config_setup import (
    load_config,
)
from automate_auth import (
    perform_login,
    update_session_file,
    decrypt_credentials,
    relogin,
    inject_cookies,
)
from automate_scrape import perform_human_actions
from automate_scrape import (
    LIKE_COUNT,
    COMMENT_COUNT,
    FOLLOW_COUNT,
    HOURLY_FOLLOW_COUNT,
    LAST_RESET,
    LAST_HOURLY_RESET,
)
from utils import sleep_with_progress_bar
from automate_tags import DEFAULT_TAGS
from automate_device import DEVICE_INFO
from automate_notification import LogLevel, AlertType, send_slack_message
from instagrapi.exceptions import (
    LoginRequired,
)

console = Console()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# Signal handler to catch keyboard interrupts
def signal_handler(sig, frame):
    console.print(
        "\n[bold red]KeyboardInterrupt detected! Exiting gracefully...[/bold red]"
    )
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


# Function to get the latest JSON session file created by config_setup.py
def get_latest_json_file(directory):
    try:
        json_files = [
            f
            for f in os.listdir(directory)
            if f.endswith("_session.json")
            and os.path.isfile(os.path.join(directory, f))
        ]
        if not json_files:
            raise FileNotFoundError("No JSON session files found in the directory.")

        # Sort the files by modification time, with the most recent first
        json_files.sort(
            key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True
        )

        # Return the full path to the most recent JSON file
        return os.path.join(directory, json_files[0])
    except Exception as e:
        logging.error(f"Error finding JSON session file: {e}")
        return None


# Load configuration
try:
    # Automatically select the most recent session file and config file
    session_directory = "./user_sessions/"
    latest_json_file = get_latest_json_file(session_directory)

    if latest_json_file:
        # Extract the username from the filename (e.g., username_session.json -> username)
        filename = os.path.basename(latest_json_file)
        if "_session.json" in filename:
            last_username = filename.replace("_session.json", "")
            logging.info(
                f"Extracted username '{last_username}' from session file name."
            )
        else:
            raise ValueError(
                "Session file name does not follow the expected format 'username_session.json'."
            )

        config = load_config(last_username)
        logging.info(
            f"Loaded configuration for user: {last_username} from session file: {latest_json_file}"
        )
    else:
        raise FileNotFoundError("No JSON session files available to load.")

    # Verify that the corresponding config file exists
    config_file = os.path.join("configs", f"{last_username}_config.yaml")
    if not os.path.exists(config_file):
        logging.error(
            f"Config file {config_file} not found. Please run config_setup.py first to generate the configuration file."
        )
        raise FileNotFoundError(f"Config file {config_file} not found")

except (FileNotFoundError, ValueError) as e:
    console.print(
        f"[bold red]Error: {e}. Make sure to run config_setup.py first to generate the configuration file.[/bold red]"
    )
    sys.exit(1)


# Decrypt Instagram credentials
INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD = decrypt_credentials(config)
logging.info("Decrypted Instagram credentials")

# Initialize Instagram client
cl = Client(DEVICE_INFO)

# Set delay range to mimic human behavior
cl.delay_range = [2, 5]

# Set proxy if available in configuration
proxy = config.get("proxy")
# if proxy:
#     cl.set_proxy(proxy)

# Perform initial login
session_file = os.path.join("user_sessions", f"{INSTAGRAM_USERNAME}_session.json")
perform_login(cl, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, session_file)
update_session_file(cl, session_file)
logging.info("Logged in to Instagram")

# Inject cookies for public requests (if needed)
inject_cookies(cl, session_file)


def handle_rate_limit(client, func, *args, **kwargs):
    """Handle rate limits and re-login if needed, with exponential backoff."""
    retries = 3
    for attempt in range(retries):
        try:
            console.print(
                f"[bold blue]Attempting call {attempt+1}/{retries}[/bold blue]"
            )
            return func(*args, **kwargs)
        except Exception as e:
            console.print(
                f"[bold red]Error on attempt {attempt+1}/{retries}[/bold red]"
            )
            console.print(f"Error message: {e}")
            if "429" in str(e) or "login_required" in str(
                e
            ):  # Rate limit or login required error
                sleep_time = min(2**attempt, 300)  # Exponential backoff up to 5 minutes
                console.print(
                    f"Rate limit or login required. Retrying in {sleep_time} seconds..."
                )
                time_sleep(sleep_time)
                console.print(
                    f"[bold yellow]Re-logging in after attempt {attempt+1}[/bold yellow]"
                )
                relogin(client, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, session_file)
            else:
                logging.error(f"Error: {e}")
                raise e
    raise Exception("Max retries exceeded")


def test_proxy(client):
    try:
        # Instagram API를 통해 공개 프로필 정보 가져오기
        username = "instagram"  # 테스트용 공개 계정
        user_info = client.user_info_by_username(username)
        print(f"Successfully fetched info for user: {username}")
        print(f"Follower count: {user_info.follower_count}")
        
        # 프록시를 통한 현재 IP 확인 (외부 서비스 사용)
        response = requests.get("https://api.ipify.org?format=json", proxies=client.private.proxies)
        ip = response.json()['ip']
        print(f"Current IP address (through proxy): {ip}")

    except Exception as e:
        print(f"Error occurred: {e}")


def main():
    try:
        # proxy server test
        cl.set_proxy(proxy)
        test_proxy(cl)
        

    except KeyboardInterrupt:
        console.print("\n[bold red]Exiting program...[/bold red]")
    except LoginRequired:
        relogin(cl, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, session_file)


if __name__ == "__main__":
    main()
