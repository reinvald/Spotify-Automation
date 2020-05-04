# Spotify Automation

This is a simple Python script inspired by and based off of TheComeUp's implementation on YouTube. This was my first time dealing with the YouTube Data and Spotify APIs, so this was mostly done for fun. This script simply takes your five most recent liked videos on YouTube, checks for songs in the video, and adds them to a designated Spotify playlist.

## Usage

Make sure to have your own Spotify user handy as well as a fresh OAuth token (which expires every hour). For the YouTube Data API calls to work, you'll need to reference your own client_secret JSON file in the code. Make sure all dependencies and packages used in the code are installed. Afterwards, the script can be run from main.py.

```bash
python main.py
```
