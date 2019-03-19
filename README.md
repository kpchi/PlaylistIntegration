# PlaylistIntegration

This python script allows you to combine multiple Spotify playlists, sorting the tracks by their date added in each playlist.  The end goal is to create one single chronological playlist of all your songs.

I have listed the permissions requested, and what they are required for:
```
playlist-modify-private: Creating or modifying a private playlist.
playlist-read-collaborative: Reading collaborative playlists.
playlist-read-private: Read access to your private playlists. 
user-library-read: Read access to 'Songs' under 'Your Library'
```

Please ensure you have filled out the following in the credentials.txt.  These are used to authenticate your account with Spotify.  

```
username=<Your Spotify numeric username>
client_id=<Your client ID>
client_secret=<Your client secret>
redirect_uri=<Your redirect uri>
```
Your Spotify numeric username can be found using the Share your profile link, and it should be after "http://open.spotify.com/user/".  The other 3 fields can be found [here](https://developer.spotify.com/dashboard/applications/).