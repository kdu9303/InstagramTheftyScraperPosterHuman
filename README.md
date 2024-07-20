### README for InstagramTheftyScraperPosterHuman

# InstagramTheftyScraperPosterHuman

## See Changes Here: [Enhanced Breakdown of Changes in InstagramTheftyScraperPosterHuman](https://github.com/sujay1599/InstagramTheftyScraperPosterHuman/wiki/Enhanced-Breakdown-of-Changes)

InstagramTheftyScraperPosterHuman is an advanced tool for automating the process of scraping, uploading, and managing Instagram reels. This tool builds upon previous versions, introducing several enhancements and new functionalities to improve automation, human-like interactions, and bot detection prevention.

## Features

### Core Features

- **Scraping Reels**: Scrapes reels from specified Instagram profiles.
- **Uploading Reels**: Uploads scraped reels with customizable descriptions and hashtags.
- **Human-like Actions**: Performs random actions like liking, commenting, and following to mimic human behavior.
- **Dashboard**: Displays detailed information about activities.
- **Anti-Bot Detection**: Implements random waits and actions to avoid detection.
- **Logging**: Logs all activities for better traceability and debugging.
- **Configurable Settings**: Uses a YAML configuration file for easy customization.

### New Features in InstagramTheftyScraperPosterHuman

- **Enhanced Random Waits**: Added random waits between scraping, liking, commenting, and uploading actions to better simulate human behavior and reduce the risk of detection by Instagram.
- **Logging of Random Waits**: Logged random wait times into a separate file (`random-waits.json`) for better tracking and debugging.
- **Detailed Logging of Comments**: The program now logs the actual comments posted on each reel for better traceability.
- **Improved Error Handling**: Enhanced error handling and logging to capture JSONDecodeError and other exceptions, making the script more robust.
- **Improved Dashboard**: Updated dashboard to display detailed information about scraping, uploading, and random wait times, as well as the next file to be uploaded.
- **Human-like Interactions**: Performs random human-like actions during waiting periods, including liking and commenting on random posts from popular hashtags.

## Requirements

- Python 3.6+
- Required Python packages (specified in `requirements.txt`)

### Install Required Packages

You can install all the required packages using the following command:

```bash
pip install -r requirements.txt
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/sujay1599/InstagramTheftyScraperPosterHuman.git
   cd InstagramTheftyScraperPosterHuman
   ```

2. Install the required packages using `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

3. Run `config_setup.py` to create the `config.yaml` file:
   ```bash
   python config_setup.py
   ```
   Follow the prompts to enter your configuration details. This will generate a `config.yaml` file with the necessary settings, including encrypted Instagram credentials.

### Configuration

The `config.yaml` file will be generated by running `config_setup.py`. It includes the following settings:

```yaml
instagram:
  username: ENCRYPTED_USERNAME
  password: ENCRYPTED_PASSWORD
key: ENCRYPTION_KEY
scraping:
  enabled: true
  profiles: profile1 profile2
  num_reels: 10
  scrape_interval_minutes: 60
  like_reels: true
uploading:
  enabled: true
  upload_interval_minutes: 30
  add_to_story: true
description:
  use_original: true
  custom_description: ""
hashtags:
  use_hashtags: true
  hashtags_list: "example hashtags"
credit:
  give_credit: true
leave_comment: true
comments:
  - "Nice reel!"
  - "Great post!"
deleting:
  delete_interval_minutes: 1440
custom_tags:
  - instagram
  - instadaily
  - LikeForFollow
  - LikesForLikes
  - LikeForLikes
  - FollowForFollow
  - LikeForLike
  - FollowForFollowBack
  - FollowBack
  - FollowMe
  - instalike
  - comment
  - follow
  - memes
  - funnymemes
  - memestagram
  - dankmemes
  - memelord
  - instamemes
  - instagood
  - love
  - photooftheday
  - picoftheday
  - likeforlikes
  - likes
  - followme
  - photography
  - beautiful
  - fashion
  - smile
  - me
  - followforfollowback
  - l
  - likeforfollow
  - myself
  - likeforlike
  - bhfyp
  - f
  - followback
  - followers
  - followforfollow
  - style
  - photo
  - happy
  - instamood
  - nature
  - trending
  - art
  - india
  - viral
  - explore
  - model
  - travel
```

### Configuration Details

- **Instagram Credentials**: Provide your Instagram username and password. These will be encrypted and stored securely.
- **Scraping Settings**:
  - `enabled`: Set to `true` to enable scraping.
  - `profiles`: Space-separated list of Instagram profiles to scrape reels from.
  - `num_reels`: Number of reels to scrape per profile.
  - `scrape_interval_minutes`: Interval in minutes between scraping sessions.
- **Uploading Settings**:
  - `enabled`: Set to `true` to enable uploading.
  - `upload_interval_minutes`: Interval in minutes between uploads.
  - `add_to_story`: Set to `true` to add reels to your Instagram story.
- **Description Settings**:
  - `use_original`: Set to `true` to use the original reel description. If `false`, you will be prompted to enter a custom description.
  - `custom_description`: The custom description to use if `use_original` is `false`.
- **Hashtags Settings**:
  - `use_hashtags`: Set to `true` to use hashtags in the reel descriptions.
  - `hashtags_list`: List of hashtags to include in the reel descriptions (if `use_hashtags` is `true`).
- **Credit Settings**:
  - `give_credit`: Set to `true` to give credit to the original poster in the reel descriptions.
- **Deleting Settings**:
  - `delete_interval_minutes`: Interval in minutes between deletions.
- **Comments**:
  - `leave_comment`: Set to `true` to leave comments on scraped videos.
  - `comments`: List of comments to leave if `leave_comment` is `true`.
- **Custom Tags**: List of custom tags for human-like actions.

## Usage

Run the script:

```bash
python main.py
```

This will start the process of scraping, uploading, and performing human-like actions as configured in the `config.yaml` file.

## Anti-Bot Detection

The program includes several features to avoid detection by Instagram:

- **Random Waits**: Implements random waits between actions to mimic human behavior.
- **Human-like Actions**: Performs random actions like liking, commenting, and following during the waiting periods.
- **Detailed Logging**: Logs all activities for better traceability and debugging.

### Logging

The script maintains several log files to track activities and debug issues:

- **upload_log.txt**: Keeps track of uploaded reels.
- **status.json**: Tracks the last action times and other status information.
- **random-upload-times.json**: Logs the random sleep times between uploads.
- **random-waits.json**: Logs the random wait times between various actions.

### Dashboard

Run the dashboard script to view detailed information about scraping, uploading activities, and random wait times:

```bash
python dashboard.py
```

### Additional Information

- **Next File to Upload**: Displays the next file to be uploaded.
- **Random Wait Times**: Shows the logged random wait times to provide insight into the randomness of actions.
- **Detailed Status**: Provides a detailed view of the last and next scrape, upload, and delete times.

### License

This project is licensed under the MIT License. See the LICENSE file for details.

### Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

### Disclaimer

This script is intended for educational and personal use only. Use it responsibly and ensure you comply with Instagram’s terms of service and guidelines.

---

### Files

Here are the uploaded files for reference:

1. **auth.py**
2. **config_setup.py**
3. **dashboard.py**
4. **input_helpers.py**
5. **main.py**
6. **requirements.txt**
7. **scrape.py**
8. **upload.py**
9. **utils.py**

## Detailed Breakdown of Files

### auth.py

Handles Instagram authentication and session management. It decrypts stored credentials and manages login sessions.

### config_setup.py

Generates the `config.yaml` configuration file with encrypted credentials. It prompts the user for inputs and creates a secure configuration file.

### dashboard.py

Displays a detailed dashboard of activities, showing the status of scraping, uploading, and human-like actions.

### input_helpers.py

Contains helper functions for getting user inputs during configuration setup.

### main.py

The main script that orchestrates the scraping, uploading, and human-like actions processes. It reads the configuration, manages the workflow, and ensures periodic actions are performed.

### scrape.py

Handles scraping of Instagram reels and performing human-like actions like liking and commenting on random posts from popular hashtags.

### upload.py

Handles uploading of scraped reels, adding them to stories if configured, and performing human-like actions during the waiting period.

### utils

.py

Contains utility functions for logging, status management, random sleeps, and managing JSON files for random wait times.

---

By using this README, you should be able to set up and run the InstagramTheftyScraperPosterHuman with ease, leveraging its advanced features for automating Instagram interactions while avoiding detection. Enjoy automating your Instagram activities responsibly!
