from spotify_api import SpotifyAPI

try:

    #opens an instance of SpotifyAPI class
    spotify = SpotifyAPI()

    #retrieves an access token from Spotify 
    spotify.get_token()

    #returns a list of all Spotify genres 
    spotify.get_genres()

    #for each genre, add artists to a dictionary
    spotify.add_artists()

except Exception as e:
    print(f"An error occurred: {e}")