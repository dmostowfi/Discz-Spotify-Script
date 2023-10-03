# this file runs unittests on both async and  
# sync methods from the SpotifyScraper() class 

import unittest
from unittest.mock import patch #for mock errors
import aiohttp
from spotify_api import SpotifyScraper

class SpotifyTestCases(unittest.IsolatedAsyncioTestCase):
    
    #open SpotifyScraper class
    def setUp(self):
        self.spotify = SpotifyScraper()
        self.token = self.spotify.get_token()

    def test_singleton(self):
        new_instance = SpotifyScraper()
        self.assertEqual(self.spotify, new_instance)

    #get_token returns a token
    def test_get_token_returns_token(self):
        self.assertIsNotNone(self.spotify.token)

    #get_genres returns a set of genres
    async def test_get_genres_returns_set(self):
        await self.spotify.get_genres()
        self.assertIs(type(self.spotify.genres_set), set)

    #niche_genres > get_genres set
    async def test_more_niche_genres(self):
        await self.spotify.get_genres()
        genres_len = len(self.spotify.genres_set)
        await self.spotify.get_niche_genres()
        niche_len = len(self.spotify.more_genres_set)
        self.assertGreater(niche_len, genres_len)


    #commented out because runs for too long, but passes
    #adds to dictionary based on genres
    #async def test_adding_to_dict_genres(self):
    #    await self.spotify.get_genres()
    #    await self.spotify.add_artists(self.spotify.genres_set, 'genre')
    #    self.assertIs(type(self.spotify.artist_data), dict)
    #    self.assertGreater(len(self.spotify.artist_data), 10)

# runs the tests
if __name__ == '__main__':
    unittest.main()