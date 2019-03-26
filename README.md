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
* Please ensure you have exported the following environment variables before running the script.  These are used to authenticate your account with Spotify.  
```
On Windows
----------
set pi_username=<Your Spotify numeric username>
set client_id=<Your client ID>
set client_secret=<Your client secret>
set redirect_uri=<Your redirect uri>

On *nix
----------
export pi_username=<Your Spotify numeric username>
export client_id=<Your client ID>
export client_secret=<Your client secret>
export redirect_uri=<Your redirect uri>
```
Your Spotify numeric username can be found using the Share your profile link, and it should be after "http://open.spotify.com/user/".  The other 3 fields can be found [here](https://developer.spotify.com/dashboard/applications/).


## Running the script
Please ensure you have exported the relevant environment variables!
```
python main.py
```