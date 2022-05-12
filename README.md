# Tweego

Generate second order ego networks for users from Twitter. Create egocentric graphs with the twitter api. Tweego allows you to resume data collection over multiple sessions.

# Usage

## Installation

```
pip install tweego
```

## CLI

```
tweego [OPTIONS]

Options:
  -d, --dir PATH                Directory to store data
  -k, --keys-file PATH          Location of the api keys JSON file
  -n, --screen-name TEXT        The screen name of the ego center user
  -f, --follower-limit INTEGER  Number of followers for the second order ego
  --help                        Show this message and exit.
```

### Example

```
tweego -d "dataset" -k "keys.json" -n "github"
```

## API keys format

Tweego supports multiple api keys to speed up the data collection process. The api keys should be in a JSON file with the following format.

You can get these details from the [Twitter developer website](https://developer.twitter.com/en/portal/projects-and-apps) by creating a standalone app and then generating the keys and tokens.

```json
[
    ...
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
    },
    ...
]
```

# Folder Structure

Once Tweego is done, the folder structure should look like this:

```
dir
├── users
│   ├── user_id_1.json
│   ├── user_id_2.json
│   └── ...
├── screen_name
│   ├── user_id_1
│   |   └── user_id_1.txt
│   ├── user_id_2
│   |   └── user_id_2.txt
│   └── ...
├── screen_name.txt
└── screen_name.gml
```

The `users` directory contains information about each user, the `screen_name` directory contains the follower ids of users. The `screen_name.gml` file contains the ego network and an application like `Gephi` can be used to analyze it.