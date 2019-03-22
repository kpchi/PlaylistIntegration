from datetime import datetime

import re
import spotipy
import spotipy.util as util

def main():
	# Scope / privileges and token authentication credentials
	scope = 'playlist-read-private playlist-modify-private playlist-read-collaborative user-library-read'
	username, client_id, client_secret, redirect_uri = read_credentials()

	token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)

	if token:
		spotipy_token = spotipy.Spotify(auth=token)

		# Gets all the playlists the user owns
		all_playlists = get_user_playlists(spotipy_token, username)

		# Gets the targeted playlists to sort
		target_playlists = get_target_playlists(all_playlists)

		# Get user input for playlist to add sorted songs to, create new playlist if one doesn't exist
		final_playlist = get_final_playlist(all_playlists)

		# Check if user wants saved songs added in as well
		# Check if user wants duplicate detection enabled
		# Begin process of consolidating songs in selected playlists to track_list
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
# :param sp: Spotipy object
# :param username: Spotify username
def get_user_playlists(sp, username):
	# Grab all user playlists, including private ones
	initial_playlists = sp.user_playlists(username)

	final_playlists = []

	while initial_playlists:
		for playlist in initial_playlists['items']:
			if playlist['owner']['id'] == username:
				final_playlists.append(playlist)

		if initial_playlists['next']:
			initial_playlists = sp.next(initial_playlists)
		else:
			initial_playlists = None

	return final_playlists


# Returns list of targeted user playlists IDs
# :param all_playlists: List of all playlists owned by the user
def get_target_playlists(all_playlists):
	reselect_playlists = True
	while reselect_playlists:
		counter = 0

		for playlist in all_playlists:
			print(counter, "-", playlist['name'])
			counter += 1

		print("\nTo select a playlist, please enter the playlist number(s) separated by commas:")
		while True:
			targeted_playlists = input()
			if (re.match(r"[0-9,]+$", targeted_playlists)):
				targeted_playlists = list(filter(None, targeted_playlists.split(',')))		
				break
			else:
				print('Please enter only numeric digits and the comma (,) character')

		final_playlists =[]

		print("\nYou have selected the following playlists:")
		for playlist_id in targeted_playlists:
			print(playlist_id, "-", all_playlists[int(playlist_id)].get('name'))
			final_playlists.append(all_playlists[int(playlist_id)].get('id'))

		confirmation = input("\nDo you want to choose the playlists again? y/n\n").lower()
		while True:
			if confirmation == 'y':
				break
			elif confirmation == 'n':
				reselect_playlists = False
				break
			else:
				confirmation = input("\nPlease enter only y or n").lower()

	return final_playlists


# Returns list of targeted user playlists IDs
# :param all_playlists: List of all playlists owned by the user
def get_final_playlist(all_playlists):
	


if __name__== "__main__":
	main()
