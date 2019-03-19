from datetime import datetime

import spotipy
import spotipy.util as util

def main():
	# Scope / Privileges
	scope = 'playlist-read-private playlist-modify-private playlist-read-collaborative user-library-read'
	
	# Token authentication credentials
	username, client_id, client_secret, redirect_uri = read_credentials()

	# Initialise Spotipy token
	token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)


# Reads user's credentials for Spotipy token
def read_credentials():
	username = ''
	client_id = ''
	client_secret = ''
	redirect_uri = ''

	with open('.\\credentials.txt') as fp:  
		username = fp.readline()
		client_id = fp.readline()
		client_secret = fp.readline()
		redirect_uri = fp.readline()

	return username, client_id, client_secret, redirect_uri



if __name__== "__main__":
	main()
