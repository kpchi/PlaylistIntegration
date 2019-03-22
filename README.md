# PlaylistIntegration

This python script takes all the tracks across the playlists you select, sorts them by date added, and adds them in sorted order to a single playlist.  The end goal is to create one single chronological playlist of all your songs.

I have listed the permissions requested, and what they are required for:
```
playlist-modify-private: Creating or modifying a private playlist.
playlist-read-collaborative: Reading collaborative playlists.
playlist-read-private: Read access to your private playlists. 
user-library-read: Read access to 'Songs' under 'Your Library'
```

## Getting Started

* Install [Python3](https://www.python.org/downloads/)
* Install the [Spotipy package](https://spotipy.readthedocs.io/en/latest/#installation) using:
```
pip install spotipy  OR
easy_install spotipy
```
* Please ensure you have filled out the following in the credentials.txt.  These are used to authenticate your account with Spotify.  

```
username=<Your Spotify numeric username>
client_id=<Your client ID>
client_secret=<Your client secret>
redirect_uri=<Your redirect uri>
```
Your Spotify numeric username can be found using the Share your profile link, and it should be after "http://open.spotify.com/user/".  The other 3 fields can be found [here](https://developer.spotify.com/dashboard/applications/).