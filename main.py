# this is the main file, which runs methods from the 
# SpotifyScraper() class asynchronously to perform the desired task 

import asyncio
from spotify_api import SpotifyScraper

async def run_spotify_scraper():
    try:

        #opens an instance of SpotifyAPI class
        spotify = SpotifyScraper()

        #retrieves an access token from Spotify 
        spotify.get_token()

        #run get_genres and get_categories simultaneously
        await asyncio.gather(
            spotify.get_genres(),
            spotify.get_categories()
        )

        # set up add_artists for genres and categories to run concurrently with get_niche_genres
        task_add_artists_genres = asyncio.create_task(spotify.add_artists(spotify.genres_set, 'genre'))
        task_add_artists_categories = asyncio.create_task(spotify.add_artists(spotify.categories_list, 'category'))
        task_get_niche_genres = asyncio.create_task(spotify.get_niche_genres())

        # when get_niche_genres finishes, run add_artists for genres, niche_genres, and categories concurrently
        await task_get_niche_genres
        task_add_artists_niche_genres = asyncio.create_task(spotify.add_artists(spotify.more_genres_set, 'genre'))

        await asyncio.gather(task_add_artists_genres, task_add_artists_categories, task_add_artists_niche_genres)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    asyncio.run(run_spotify_scraper())