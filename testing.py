import unittest
from spotify_api import SpotifyAPI

class SpotifyTestCases(unittest.TestCase):
    
    #open SpotifyAPI class
    def setUp(self):
        self.spotify = SpotifyAPI()
        self.token = self.spotify.get_token()

    #get_token returns a token
    def test_get_token_returns_token(self):
        self.assertIsNotNone(self.spotify.token)

    #get_genres returns a list of genres
    def test_get_genres_returns_list(self):
        self.spotify.get_genres()
        self.assertIs(type(self.spotify.genres_list), list)

    #at what point does add_artists hit rate limit?
    #writes to dictionary

# runs the tests
if __name__ == '__main__':
    unittest.main()