from spotify_api import SpotifyAPI

#opens an instance of SpotifyAPI class
spotify = SpotifyAPI()

#retrieves an access token from Spotify 
spotify.get_token()

#returns a list of all Spotify genres 
spotify.get_genres()

#for each genre, add artists to a dictionary
spotify.add_artists()