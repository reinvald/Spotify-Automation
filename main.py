import json
import requests
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import youtube_dl

from secrets import spotify_user_id, spotify_oauth_token


# main class containing all methods for interacting with Spotify/YouTube
class MainEngine:
    def __init__(self):
        self.spotify_user_id = spotify_user_id
        self.spotify_oauth_token = spotify_oauth_token
        self.youtube = self.setup_youtube()
        self.songs = {}

    # code from YouTube Data API, setups YouTube client for interaction
    def setup_youtube(self):
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "client_secret.json"

        # Get credentials and create an API client
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()
        return googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

    def fetch_videos(self):

        # queries YouTube for liked videos
        request = self.youtube.videos().list(
            part="snippet,contentDetails,statistics", myRating="like")
        response = request.execute()

        # iterate through liked videos and creates a song JSON object for each, dynamically fetching song URIs
        for v in response["items"]:
            name = v["snippet"]["title"]
            print(name)
            url = "https://www.youtube.com/watch?v={}".format(v["id"])

            video = youtube_dl.YoutubeDL({}).extract_info(url, download=False)

            song = video["track"]
            artist = video["artist"]

            self.songs[name] = {
                "url": url,
                "song": song,
                "artist": artist,
                "spotify_uri": self.fetch_song(song, artist)
            }

    # creates Spotify playlist for the songs we will be searching for
    def create_spotify_playlist(self):

        # HTTP request to Spotify API
        request = json.dumps({
            "name": "songs from YouTube",
            "description": "test test test",
            "public": True
        })

        query = "https://api.spotify.com/v1/users/{}/playlists".format(
            self.spotify_user_id)

        res = requests.post(query, data=request, headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.spotify_oauth_token)
        })

        res_JSON = res.json()

        # return playlist ID
        return res_JSON["id"]

    # queries Spotify and fetches song URI
    def fetch_song(self, song, artist):

        # Spotify API query to search for a song with song name and artist name
        query = "https://api.spotify.com/v1/search?q=track%3A{}%20artist%3A{}&type=track%2Cartist&limit=20&offset=0".format(
            song, artist)

        res = requests.get(query,
                           headers={
                               "Content-Type": "application/json",
                               "Authorization": "Bearer {}".format(self.spotify_oauth_token)
                           }
                           )

        res_JSON = res.json()

        # return URI for first track returned
        if len(res_JSON["tracks"]["items"]) == 0:
            return None
        return res_JSON["tracks"]["items"][0]["uri"]

    def add_songs(self):

        playlist = self.create_spotify_playlist()

        # fill up dictionary with song and video info
        self.fetch_videos()

        all_uri = []

        for song, info in self.songs.items():
            if (info["spotify_uri"] != None):
                all_uri.append(info["spotify_uri"])

        req_data = json.dumps(all_uri)

        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
            playlist)

        res = requests.post(
            query,
            data=req_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.spotify_oauth_token)
            }
        )

        return res.json()


if __name__ == "__main__":
    me = MainEngine()
    me.add_songs()
