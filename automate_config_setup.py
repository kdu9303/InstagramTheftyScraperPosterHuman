import json
import yaml
import os
import logging
import getpass
from instagrapi import Client
from rich.console import Console
from automate_auth import (
    perform_login,
    generate_key,
    encrypt_credentials,
)  # Functions from auth.py
from automate_device import DEVICE_INFO

console = Console()

# Constants
SESSION_DIR = "user_sessions"
CONFIG_DIR = "configs"
KEY_FILE = "key.key"  # Encryption key storage


# Set up logging
logging.basicConfig(
    filename="config_setup.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Ensure the session and config directories exist
os.makedirs(SESSION_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

console.print(
    f"[bold green]Created session and config directories if not present[/bold green]"
)


# Encryption key management
def load_or_generate_key():
    """Load encryption key from file, or generate a new one if it doesn't exist."""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as key_file:
            return key_file.read()
    else:
        key = generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
        logging.info(f"Generated new encryption key: {KEY_FILE}")
        return key


# Prompt user for Instagram credentials and validate login
def get_user_credentials():
    """Prompt user for Instagram credentials and validate login via auth.py."""
    key = load_or_generate_key()
    while True:
        username = input("Enter Instagram username: ").encode()
        password = getpass.getpass("Enter Instagram password: ").encode()

        # Initialize the Client object
        client = Client(DEVICE_INFO)
        client.delay_range = [1, 3]  # Mimic human behavior
        session_file = os.path.join(SESSION_DIR, f"{username.decode()}_session.json")

        # Perform login using auth.py's function
        if perform_login(client, username.decode(), password.decode(), session_file):
            logging.info(f"Login successful for user: {username.decode()}")
            console.print("[bold green]Login successful![/bold green]")
            encrypted_username, encrypted_password = encrypt_credentials(
                username, password, key
            )
            return (
                encrypted_username,
                encrypted_password,
                username.decode(),
            )  # Return decoded username for file naming
        else:
            console.print("[bold red]Login failed. Please try again.[/bold red]")
            logging.error(f"Login failed for user: {username.decode()}")


# Create the full configuration file
def create_config(encrypted_username, encrypted_password, key, username):
    """Create the main configuration file."""
    config = {
        "instagram": {
            "username": encrypted_username,
            "password": encrypted_password,
        },
        "key": key.decode(),
        "proxy": input("Enter proxy server address (leave blank if not using proxy): "),
    }

    return config


def save_config(config, username, filename=None):
    """Save the configuration dictionary to a YAML file."""
    if filename is None:
        filename = os.path.join(
            CONFIG_DIR, f"{username}_config.yaml"
        )  # Save config for specific user

    try:
        with open(filename, "w", encoding="utf-8") as file:
            yaml.dump(config, file)
        console.print(f"[bold green]Configuration saved to {filename}[/bold green]")
        logging.info(f"Configuration saved to {filename}")
    except Exception as e:
        console.print(f"[bold red]Failed to save configuration: {e}[/bold red]")
        logging.error(f"Failed to save configuration: {e}")


# Save configuration to a YAML file, using the username to differentiate files


def load_config(username, filename=None):
    """Load the configuration from a YAML file."""
    if filename is None:
        filename = os.path.join(
            CONFIG_DIR, f"{username}_config.yaml"
        )  # Use the config for specific user

    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)
            console.print(
                f"[bold green]Configuration loaded from {filename}[/bold green]"
            )
            return config
        except Exception as e:
            console.print(f"[bold red]Failed to load configuration: {e}[/bold red]")
            logging.error(f"Failed to load configuration: {e}")
            raise
    else:
        console.print(
            f"[bold red]Configuration file {filename} not found. Run config_setup.py first.[/bold red]"
        )
        raise FileNotFoundError(f"Configuration file {filename} not found.")


# Main function to set up the config
def main():
    """Main function to gather credentials, create, and save configuration."""
    key = load_or_generate_key()
    encrypted_username, encrypted_password, username = get_user_credentials()
    config = create_config(encrypted_username, encrypted_password, key, username)
    save_config(config, username)


if __name__ == "__main__":
    main()
