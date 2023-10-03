import asyncio
from spotify_api import SpotifyScraper

async def run_spotify_scraper():
    try:

        #opens an instance of SpotifyAPI class
        spotify = SpotifyScraper()

        #retrieves an access token from Spotify 
        spotify.get_token()

        #testing async functionality
        await spotify.get_genres()
        await spotify.get_niche_genres()
        await spotify.get_categories()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    asyncio.run(run_spotify_scraper())


#await asyncio.gather(
#    spotify.get_genres(),
#    spotify.get_categories()
#)

#await asyncio.gather(
#    spotify.add_artists(spotify.genres_list, 'genre'),
#    spotify.add_artists(spotify.categories_list, 'category')
#)

#        task_genres = asyncio.create_task(spotify.get_genres())
       # task_categories = asyncio.create_task(spotify.get_categories())

       # await task_categories
      #  task_add_artists_categories = asyncio.create_task(spotify.add_artists(spotify.categories_list, 'category'))

      #  await task_genres
      #  task_add_artists_genres = asyncio.create_task(spotify.add_artists(spotify.genres_list, 'genre'))

     #   await asyncio.gather(task_add_artists_genres, task_add_artists_categories)