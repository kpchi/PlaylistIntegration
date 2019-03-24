from datetime import datetime

import re
import spotipy
import spotipy.util as util


def main():
    # Scope / privileges and token authentication credentials
    scope = ('playlist-read-private '
             'playlist-modify-private '
             'playlist-read-collaborative '
             'user-library-read')
    username, client_id, client_secret, redirect_uri = read_credentials()

    token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)

    if token:
        spotipy_token = spotipy.Spotify(auth=token)

        # Gets all the playlists the user owns
        all_playlists = get_user_playlists(spotipy_token, username)

        # Gets the targeted playlists to sort
        target_playlists = get_target_playlists(all_playlists)

        # Gets playlist to add sorted songs to, creates new playlist if one doesn't exist
        final_playlist = get_final_playlist(spotipy_token, username, all_playlists)

        # Check if user wants saved songs added in and duplicate detection enabled
        var_saved_songs, var_dup_detect = get_user_preferences()

        # Begin process of consolidating songs in selected playlists to track_list
        get_sorted_tracks(spotipy_token, username,
                          target_playlists, var_saved_songs, var_dup_detect)

        # Add saved songs to consolidated track_list
        # If duplicate detection is enabled, remove duplicated tracks from track_list
        # Sort track_list, converting to dictionary first, then return list of sorted track IDs
        # Add list of sorted track IDs to target final playlist, chunking them into sets of 75
    else:
        print("Unable to create Spotipy token")


# Reads user's credentials for Spotipy token
def read_credentials():
    username = ''
    client_id = ''
    client_secret = ''
    redirect_uri = ''

    with open('.\\credentials.txt') as fp:
        username = fp.readline().rstrip().split('=')[1]
        client_id = fp.readline().rstrip().split('=')[1]
        client_secret = fp.readline().rstrip().split('=')[1]
        redirect_uri = fp.readline().rstrip().split('=')[1]

    return username, client_id, client_secret, redirect_uri


# Returns list of all playlists owned by the user
# :param spotipy_token: Spotipy object
# :param username: Spotify username
def get_user_playlists(spotipy_token, username):
    # Grab all user playlists, including private ones
    initial_playlists = spotipy_token.user_playlists(username)

    final_playlists = []

    while initial_playlists:
        for playlist in initial_playlists['items']:
            if playlist['owner']['id'] == username:
                final_playlists.append(playlist)

        if initial_playlists['next']:
            initial_playlists = spotipy_token.next(initial_playlists)
        else:
            initial_playlists = None

    return final_playlists


# Returns list of targeted user playlists IDs
# :param all_playlists: List of all playlists owned by the user
def get_target_playlists(all_playlists):
    while True:
        print_playlists(all_playlists)

        print("\nTo select a playlist, please enter the playlist number(s) separated by commas:")

        while True:
            targeted_playlists = input()
            if re.match(r"[0-9,]+$", targeted_playlists):
                targeted_playlists = list(filter(None, targeted_playlists.split(',')))

                if all(int(item) <= (len(all_playlists) - 1) for item in targeted_playlists):
                    break
                else:
                    print("Please enter a valid number within the range of playlists")
            else:
                if not targeted_playlists:
                    print("Please select a playlist")
                else:
                    print('Please enter only numeric digits and the comma (,) character:')

        final_playlists = []

        print("\nYou have selected the following playlists:")
        for playlist_id in targeted_playlists:
            print(playlist_id, "-", all_playlists[int(playlist_id)].get('name'))
            final_playlists.append(all_playlists[int(playlist_id)].get('id'))

        if not confirm_yesno("Do you want to choose the playlists again?"):
            break

    return final_playlists


# Prints out a numeric list of playlists
# :param playlists: List of playlist objects to be printed out
def print_playlists(playlists):
    for playlist_id, playlist in enumerate(playlists):
        print("{} - {}".format(playlist_id, playlist['name']))


# Returns True/False based on yes/no input
# :param question: Question to display
def confirm_yesno(question):
    confirmation = input("\n" + question + " y/n\n").lower()
    while True:
        if confirmation == 'y':
            confirmation = True
            break
        elif confirmation == 'n':
            confirmation = False
            break
        else:
            confirmation = input("\nPlease enter only y or n\n").lower()

    return confirmation


# Returns ID of targeted final playlist
# :param spotipy_token: Spotipy object
# :param username: Spotify username
# :param all_playlists: List of all playlists owned by the user
def get_final_playlist(spotipy_token, username, all_playlists):
    print_playlists(all_playlists)

    targeted_playlist = ""

    print("\nSelect the final playlist to store the sorted songs into",
          "or enter new to create a new playlist:")
    while True:
        targeted_playlist = input()
        if not targeted_playlist.strip():
            print("Please select a playlist")
        elif targeted_playlist == "new":
            print("\nPlease enter the name of the new playlist:")
            while True:
                targeted_playlist = input()
                if not targeted_playlist.strip():
                    print("Please enter a playlist name")
                    continue
                else:
                    break

            targeted_playlist = create_final_playlist(spotipy_token, username, targeted_playlist)
            break
        elif (len(targeted_playlist) <= 2 and targeted_playlist.isdigit()):
            if int(targeted_playlist) > (len(all_playlists) - 1):
                print("Please enter a valid number within the range of playlists")
                continue
            else:
                targeted_playlist = all_playlists[int(targeted_playlist)].get('id')

            break
        else:
            print('Please enter only numeric digits and the comma (,) character, or new only:')

    return targeted_playlist


# Returns ID of created final playlist
# :param spotipy_token: Spotipy object
# :param username: Spotify username
def create_final_playlist(spotipy_token, username, playlist_name):
    playlist_description = "Chronological list of sorted playlists created on "
    playlist_description += str(datetime.now().strftime("%d/%m/%Y at %H:%M:%S"))
    final_playlist = spotipy_token.user_playlist_create(username, playlist_name, public=False,
                                                        description=playlist_description)

    return final_playlist.get('id')


# Returns user preference for adding saved songs and duplicate detection
def get_user_preferences():
    pref_saved_songs = bool(confirm_yesno("Do you want to add your saved 'Songs' in 'Your Library'?"))
    pref_dup_detect = bool(confirm_yesno("Do you want to remove duplicates from the final sorted playlist?"))

    return pref_saved_songs, pref_dup_detect


# Returns a consolidated list of track IDs
# :param spotipy_token: Spotipy object
# :param username: Spotify username
# :param playlist_ids: List of playlist IDs
# :param var_saved_songs: Add in saved songs?
# :param var_dup_detect: Remove duplicates?
def get_sorted_tracks(spotipy_token, username, playlist_ids, var_saved_songs, var_dup_detect):
    final_tracks = []
    # First get tracks from each individual playlist
    for playlistid in playlist_ids:
        final_tracks.extend(get_tracks_from_playlist(spotipy_token, username, playlistid))
    #print("No. of tracks", len(final_tracks))
    # Then add saved songs if required
    if var_saved_songs:
        final_tracks.extend(get_saved_songs(spotipy_token))
        #print("No. of tracks w/ saved songs", len(final_tracks))

    # Then do duplicate detection
    #if var_dup_detect:
    #

    # Then sort the remaining tracks


# Returns a list of tracks from a specified playlist
# :param spotipy_token: Spotipy object
# :param username: Spotify username
# :param playlist_ids: List of playlist IDs
def get_tracks_from_playlist(spotipy_token, username, playlist_ids):
    # Grabs all songs from specified playlist, limit of 50 per round
    results = spotipy_token.user_playlist(username, playlist_ids, fields='tracks, next')
    temp_tracks = results['tracks']

    final_tracks = get_tracks_from_playlist_helper(temp_tracks)

    # If limit of 50 is hit, loop to next 50 tracks
    while temp_tracks['next']:
        temp_tracks = spotipy_token.next(temp_tracks)

        final_tracks.extend(get_tracks_from_playlist_helper(temp_tracks))

    return final_tracks


# Helper function that returns a list of tracks from a playlist object
# :param results: Spotipy playlist object containing tracks
def get_tracks_from_playlist_helper(results):
    track_results = []

    for i, track in enumerate(results['items']):
        track_results.append(track)

    return track_results


# Returns user's saved songs
# :param spotipy_token: Spotipy object
def get_saved_songs(spotipy_token):
    # Grabs all of users saved tracks, limit of 50 per round
    results = spotipy_token.current_user_saved_tracks()
    saved_songs = []

    while results:
        for item in results['items']:
            saved_songs.append(item)
        # If limit of 50 is hit, loop to next 50 saved songs
        if results['next']:
            results = spotipy_token.next(results)
        else:
            results = None

    return saved_songs


if __name__ == "__main__":
    main()
