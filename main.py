"""Script for chronologically sorting Spotify playlists"""
from datetime import datetime

import os
import re
import keyring
import spotipy
import spotipy.util as util

# Chunk size set to 80 to account for Spotify API limit of adding 75 - 100 songs per call.
SPOTIPY_MAX_TRACKS_PER_ADD = 80

def main():
    """Main function, runs all the code."""

    # Scope / privileges and token authentication credentials
    scope = ("playlist-read-private "
             "playlist-modify-private "
             "playlist-modify-public "
             "playlist-read-collaborative "
             "user-library-read")

    username, token = get_spotipy_token(scope)

    if token is None:
        print("Unable to create Spotipy token.")
        return

    spotipy_object = spotipy.Spotify(auth=token)

    # Check if user wants saved songs added in and duplicate detection enabled
    add_saved_songs, do_dup_detect = get_user_preferences()

    # Gets all the playlists the user owns
    all_playlists = get_user_playlists(spotipy_object, username)

    # Gets the targeted playlists to sort
    target_playlists = get_target_playlists(all_playlists)

    # Gets playlist to add sorted songs to, creates new playlist if one doesn'1t exist
    final_playlist = get_final_playlist(spotipy_object, username, all_playlists)

    # Begin process of consolidating songs in selected playlists to track_list
    sorted_tracks = get_sorted_tracks(spotipy_object, username, target_playlists,
                                      add_saved_songs, do_dup_detect)

    # Add list of sorted track IDs to target final playlist, chunking them into sets of 75
    add_tracks_to_final_playlist(spotipy_object, username, final_playlist, sorted_tracks)


def get_spotipy_token(scope):
    """Gets and returns an authenticated Spotipy token from keyring.

    Parameters:
        scope: String of allowed scopes

    Returns:
        String username and the authenticated Spotipy token.
    """

    username = keyring.get_password("playlistintegration", "pi_username")
    client_id = keyring.get_password("playlistintegration", "client_id")
    client_secret = keyring.get_password("playlistintegration", "client_secret")
    redirect_uri = keyring.get_password("playlistintegration", "redirect_uri")

    if (not username) or (not client_id) or (not client_secret) or (not redirect_uri):
        username = os.getenv("pi_username")
        client_id = os.getenv("client_id")
        client_secret = os.getenv("client_secret")
        redirect_uri = os.getenv("redirect_uri")
        keyring.set_password("playlistintegration", "pi_username", username)
        keyring.set_password("playlistintegration", "client_id", client_id)
        keyring.set_password("playlistintegration", "client_secret", client_secret)
        keyring.set_password("playlistintegration", "redirect_uri", redirect_uri)

    token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)

    return username, token


def get_user_preferences():
    """Reads user's credentials for Spotipy token from credentials.txt.

    Parameters:
        None

    Returns:
        Boolean representation of user's reply to adding saved songs and
        enabling duplicate detection.
    """

    add_saved_songs = bool(confirm_yesno(
        "Do you want to add your saved 'Songs' in 'Your Library'?"))
    do_dup_detect = bool(confirm_yesno(
        "Do you want to remove duplicates from the final sorted playlist?"))

    return add_saved_songs, do_dup_detect


def get_user_playlists(spotipy_obj, username):
    """Gets and returns all Spotify playlists owned by the username specified.

    Parameters:
        spotipy_obj: Spotipy object
        username: Spotify username

    Returns:
        List of dictionaries, each dictionary a Spotify playlist object.

    """

    # Grab all user playlists, including private ones
    initial_playlists = spotipy_obj.user_playlists(username)

    final_playlists = []

    while initial_playlists:
        for playlist in initial_playlists["items"]:
            if playlist["owner"]["id"] == username:
                final_playlists.append(playlist)

        if initial_playlists["next"]:
            initial_playlists = spotipy_obj.next(initial_playlists)
        else:
            initial_playlists = None

    return final_playlists


def get_target_playlists(all_playlists):
    """Takes in user input to select playlists to consolidate.

    Users can choose to reselect playlists if they have forgotten to add playlists.

    Parameters:
        all_playlists: List of all playlists owned by the user

    Returns:
        List of user playlist IDs.
    """

    final_playlists = []

    while True:
        print_playlists(all_playlists)

        print("\nTo select a playlist, please enter the playlist number(s) separated by commas:")

        while True:
            targeted_playlists = input()
            if re.match(r"[0-9,]+$", targeted_playlists):
                # Splits and filters out the empty case when an input ends with a ,
                targeted_playlists = list(filter(None, targeted_playlists.split(",")))

                if all(int(item) <= (len(all_playlists) - 1) for item in targeted_playlists):
                    break
                else:
                    print("Please enter a valid number within the range of playlists")
            else:
                if not targeted_playlists:
                    print("Please select a playlist")
                else:
                    print("Please enter only numeric digits and the comma (,) character:")

        print("\nYou have selected the following playlists:")
        for playlist_id in targeted_playlists:
            print(playlist_id, "-", all_playlists[int(playlist_id)].get("name"))
            final_playlists.append(all_playlists[int(playlist_id)].get("id"))

        if not confirm_yesno("Do you want to choose the playlists again?"):
            break

        final_playlists = []

    return final_playlists


def print_playlists(playlists):
    """Prints out an itemized list of playlists

    Users can choose to reselect playlists if they have forgotten to add playlists.

    Parameters:
        playlists: List of playlist objects to be printed out.
    """

    print("")
    for playlist_id, playlist in enumerate(playlists):
        print("{} - {}".format(playlist_id, playlist["name"]))


def confirm_yesno(question):
    """Gets user's reply to yes/no confirmation.

    Parameters:
        question: String containing question to be displayed

    Returns:
        Boolean representation of user's reply to question.
    """

    result = False
    response = input("\n" + question + " y/n\n").lower()

    while True:
        if response == "y":
            result = True
            break
        elif response == "n":
            result = False
            break
        else:
            response = input("\nPlease enter only y or n.\n").lower()

    return result


def get_final_playlist(spotipy_obj, username, all_playlists):
    """Gets and returns the final Spotify playlist ID.

    Parameters:
        spotipy_obj: Spotipy object
        username: Spotify username
        all_playlists: List of all playlists owned by the user

    Returns:
        String of final playlist ID.

    """

    print_playlists(all_playlists)

    print("\nSelect a playlist to store the sorted songs into or",
          "enter new to create a new playlist:")
    while True:
        targeted_playlist = input()
        if not targeted_playlist.strip():
            print("\nPlease select a playlist")
        elif targeted_playlist == "new":
            targeted_playlist = input("\nPlease enter the name of the new playlist:\n")
            while True:
                if not targeted_playlist.strip():
                    targeted_playlist = input("\nPlease enter a playlist name\n")
                    continue
                else:
                    break

            targeted_playlist = create_final_playlist(spotipy_obj, username, targeted_playlist)

            break
        elif targeted_playlist.isdigit():
            if int(targeted_playlist) > (len(all_playlists) - 1):
                print("\nPlease enter a valid number less than  "
                      + str(len(all_playlists) - 1) + ":")
                continue
            else:
                targeted_playlist = all_playlists[int(targeted_playlist)].get("id")

            break
        else:
            print("\nPlease enter only numeric digits and the comma (,) character, or new only:")

    return targeted_playlist


def create_final_playlist(spotipy_obj, username, playlist_name):
    """Creates and returns ID of new final playlist.

    Parameters:
        spotipy_obj: Spotipy object
        username: Spotify username
        playlist_name: String containing playlist name to be created

    Returns:
        String ID of final playlist created.
    """

    playlist_description = "Chronological list of sorted playlists created on "
    playlist_description += str(datetime.now().strftime("%d/%m/%Y at %H:%M:%S"))
    final_playlist = spotipy_obj.user_playlist_create(username, playlist_name, public=False,
                                                      description=playlist_description)

    return final_playlist.get("id")


def get_sorted_tracks(spotipy_obj, username, playlist_ids, add_saved_songs, do_dup_detect):
    """Gets and returns a list of consolidated track IDs.

    This function gets all tracks from the specified playlists, before checking to
    add the user's saved songs.  It then sorts the resulting list before doing
    duplicate detection.

    Parameters:
        spotipy_obj: Spotipy object
        username: Spotify username
        playlist_ids: List of playlist IDs
        add_saved_songs: Add in saved songs?
        do_dup_detect: Remove duplicates?

    Returns:
        List of consolidated track IDs.
    """

    final_tracks = []

    for playlistid in playlist_ids:
        final_tracks.extend(get_tracks_from_playlist(spotipy_obj, username, playlistid))
        #print("No. of tracks", len(final_tracks))

    if add_saved_songs:
        final_tracks.extend(get_saved_songs(spotipy_obj))
        #print("No. of tracks w/ saved songs", len(final_tracks))

    # First sort all the tracks
    sorted_tracks = sorted(final_tracks,
                           key=lambda k: datetime.strptime(k["added_at"], "%Y-%m-%dT%H:%M:%SZ"))

    if do_dup_detect:
        sorted_tracks = remove_duplicate_tracks(sorted_tracks)

    return sorted_tracks


def get_tracks_from_playlist(spotipy_obj, username, playlist_ids):
    """Gets and returns tracks from a given list of playlists.

    Parameters:
        spotipy_obj: Spotipy object
        username: Spotify username
        playlist_ids: List of playlist IDs

    Returns:
        List of all Spotipy track objects from a given set of playlist IDs.
    """

    results = spotipy_obj.user_playlist(username, playlist_ids, fields="tracks, next")
    temp_tracks = results["tracks"]

    final_tracks = temp_tracks["items"]

    while temp_tracks["next"]:
        temp_tracks = spotipy_obj.next(temp_tracks)

        final_tracks.extend(temp_tracks["items"])

    return final_tracks


def get_saved_songs(spotipy_obj):
    """Gets all of the user's saved songs.

    Parameters:
        spotipy_obj: Spotipy object

    Returns:
        List of all of the user's saved songs.
    """

    results = spotipy_obj.current_user_saved_tracks()
    saved_songs = []

    while results:
        for item in results["items"]:
            saved_songs.append(item)
        if results["next"]:
            results = spotipy_obj.next(results)
        else:
            results = None

    return saved_songs


def remove_duplicate_tracks(target_list):
    """Removes duplicate songs from target list.

    This function removes duplicate songs from the target list.  Duplicate removal
    is done in 2 phases.  1) Keeping only the first occurrence of a trackID and 2)
    Removing tracks which have the same Track Name and Artist Name.

    Parameters:
        target_list: List of dictionaries with sorted tracks.

    Returns:
        List of track IDs with duplicates removed.
    """

    unique_strs = set()
    unique = []

    for track in target_list:
        tracking_string = str(track.get("track").get("artists")[0].get("name")
                              + "_" + track.get("track").get("name"))
        if tracking_string not in unique_strs:
            unique.append(track)
            unique_strs.add(tracking_string)

    return unique


def add_tracks_to_final_playlist(spotipy_obj, username, final_playlist, sorted_tracks):
    """Adds sorted tracks to final playlist given.

    This is done in 3 phases.  Firstly, the sorted_tracks are converted into a list of
    trackIDs only.  Secondly, the list of trackIDs is chunked into sublists of size 75
    (this is the Spotipy add track limit per API call).  Lastly, each sublist is then
    added into the target playlist.

    Parameters:
        spotipy_obj: Spotipy object
        username: Spotify username
        final_playlist: Final Playlist ID
        sorted_tracks: List of sorted track objects.
    """

    sorted_trackids = [item.get("track").get("id") for item in sorted_tracks]

    chunked_list = list(chunks(sorted_trackids, SPOTIPY_MAX_TRACKS_PER_ADD))

    for sub_list in chunked_list:
        results = spotipy_obj.user_playlist_add_tracks(username, final_playlist,
                                                       sub_list)
        print(results)


def chunks(list_to_chunk, list_size):
    """Yields slices of the given list in the specified chunk size.

    Parameters:
        list_to_chunk: List to be chunked.
        list_size: Slice chunk size.

    Returns:
        Yields slices of specified chunk size.
    """
    # For item i in a range that is a length of list size.
    for i in range(0, len(list_to_chunk), list_size):
        # Create an index range for list_to_chunk of list_size items:
        yield list_to_chunk[i : i + list_size]


if __name__ == "__main__":
    main()
