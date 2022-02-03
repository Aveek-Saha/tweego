# Tweego

Generate ego networks for users from Twitter. Create egocentric graphs with the twitter api.

# Usage

## Installation

```
pip install tweego
```

## CLI Options

```
tweego generate-network [OPTIONS]

Options:
  -d, --dir PATH                Directory to store data
  -k, --keys-file PATH          Location of the api keys JSON file
  -n, --screen-name TEXT        The screen name of the ego center user
  -f, --follower-limit INTEGER  Number of followers for the second order ego
  --help                        Show this message and exit.
```

## API keys format

Tweego supports multiple api keys to speed up the data collection process. The api keys should be in a JSON file with the following format.

You can get these details from the Twitter developer website.

```json
[
  {
    "app_key": "<<app_key>>",
    "app_secret": "<<app_secret>>",
    "oauth_token": "<<oauth_token>>",
    "oauth_token_secret": "<<oauth_token_secret>>"
  },
  {
    "app_key": "<<app_key>>",
    "app_secret": "<<app_secret>>",
    "oauth_token": "<<oauth_token>>",
    "oauth_token_secret": "<<oauth_token_secret>>"
  }
]
```