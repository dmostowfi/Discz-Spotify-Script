#this file creates the SpotifyScraper() class, which contains the async/sync methods 
#necessary for extracting and writing artist data as well as tracking Spotify's rate limit 

import base64
import requests
import os
import time
import aiohttp
import asyncio
from collections import deque
from dotenv import load_dotenv
load_dotenv()

#class for all interactions with Spotify API
class SpotifyScraper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpotifyScraper, cls).__new__(cls)
            cls._instance._token = None
        return cls._instance

    def __init__(self):
        self.artist_data = {} #for storing artist info
        self.timestamps = deque() #for counting #API calls in 30sec
    
    # method for retrieving an access token from Spotify
    def _access_token(self):
    
        # get spotify app credentials
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")

        # encoding the credentials
        auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode('utf-8')).decode('utf-8')

        authOptions = {
            'url': 'https://accounts.spotify.com/api/token',
            'headers': {
                'Authorization': f'Basic {auth_header}'
            },
            'data': {
                'grant_type': 'client_credentials'
            }
        }

        # send request
        response = requests.post(
            authOptions['url'],
            headers=authOptions['headers'],
            data=authOptions['data']
        )
        self.api_call_counter()

        # parse response
        if response.status_code == 200:
            self.token = response.json()['access_token']

            #update the header to include the token for future API requests
            self.headers = {
                'Authorization': f'Bearer {self.token}'}

        else:
            print(f"Failed to get token: {response.content}")
            raise Exception("Failed to get token")
        
    # method for retrieving access token
    def get_token(self):
        if self._token:
            return self._token
        return self._access_token()

    # method for getting all available genres
    async def get_genres(self):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get('https://api.spotify.com/v1/recommendations/available-genre-seeds', headers=self.headers) as response:
                self.api_call_counter()
                if response.status == 200:
                    data = await response.json()
                    self.genres_list = data['genres']
                    self.genres_set = set(self.genres_list)
                else:
                    error_msg = await response.content
                    print(f'Error: {error_msg}')
                    raise Exception("Failed to get genres")
                
    #method for getting even more obscure genres
    async def get_niche_genres(self):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:                            
            #create a new set for niche genres 
            self.more_genres_set = set()
            #iterate through list of 126 genres extracted from get_genres
            for genre in self.genres_list:
                params = {
                    "q": f"genre:\"{genre}\"",
                    "type": "artist", 
                    "limit":50
                }
            async with session.get('https://api.spotify.com/v1/search', headers=self.headers, params=params) as response:
                self.api_call_counter()
                if response.status == 200:
                    data = await response.json()

                    while True:
                        artists_list = data['artists']['items']
                        for item in artists_list:
                            more_genres = item['genres']
                            if len(more_genres) == 0: pass
                            else:
                                for genre in more_genres:
                                    #don't add if already in original genres_set
                                    if genre not in self.genres_set:
                                        self.more_genres_set.add(genre)
                        #moving onto the next page
                        next_page = data['artists']['next']
                        if next_page is not None:
                            async with session.get(next_page, headers=self.headers) as response:
                                self.api_call_counter()
                                if response.status == 429:
                                    retry_after = int(response.headers.get('Retry-After', 5))
                                    print("Rate limit reached")
                                    await asyncio.sleep(retry_after)
                                    continue #TO DO - known issue: this skips the current iteration 
                                else: data = await response.json()
                        else:
                            break #reached end of items for that genre
                elif response.status == 429:                       
                    retry_after = int(response.headers.get('Retry-After', 5))
                    print("Rate limit reached")
                    await asyncio.sleep(retry_after)
                else:
                    error_msg = await response.content
                    print(f'Error: {error_msg}')
                    raise Exception("Failed to get niche genres")
        
    # method for getting categories
    async def get_categories(self):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            self.categories_list = [] 
            params = {"limit": 50}
            async with session.get('https://api.spotify.com/v1/browse/categories', headers=self.headers, params=params) as response:
                self.api_call_counter()
                if response.status == 200:
                    data = await response.json()
                    while True:
                        categories_json = data['categories']['items']
                        for item in categories_json:
                            category = item['name']
                            self.categories_list.append(category)

                        #moving onto the next page
                        next_page = data['categories']['next']
                        if next_page is not None:
                            async with session.get(next_page, headers=self.headers, params=params) as response:
                                self.api_call_counter()
                                if response.status == 429:
                                    retry_after = int(response.headers.get('Retry-After', 5))
                                    print("Rate limit reached")
                                    await asyncio.sleep(retry_after)
                                    continue #TO DO - known issue: this skips the current iteration 
                                else: data = await response.json()
                        else:
                            break #reached end of categories
                else:
                    error_msg = await response.content
                    print(f'Error: {error_msg}')
                    raise Exception("Failed to get categories")
        
    #method for counting number of API calls in a 30 second window
    def api_call_counter(self):
        current_time = time.time()
        self.timestamps.append(current_time)

        # Remove API calls that are older than 30 seconds from the front of the queue
        while self.timestamps and current_time - self.timestamps[0] > 30:
            self.timestamps.popleft()
        
        print(f"API calls in the last 30 seconds: {len(self.timestamps)}")

    #method for writing artist data to dictionary
    async def add_artists(self, l: list[str], query: str): 
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            i = 0 #for tracking how many genres we get through before hitting limit
            for item in l:
                
                #print(f"Finding artists for {item}")
                i += 1
                #print("i=", i)
                # first, call Spotify /search API, filtered on query
                if query == "genre":
                    params = {
                        "q": f"genre:\"{item}\"",
                        "type": "artist", 
                        "limit":50
                    }
                elif query == "category":
                    params = {
                        "q": f"\"{item}\"",
                        "type": "artist", 
                        "limit":50
                    }
                async with session.get('https://api.spotify.com/v1/search', headers=self.headers, params=params) as response:
                    self.api_call_counter()
                    # then, get artist data 
                    if response.status == 200:
                        data = await response.json()

                        while True:
                            #list of artists for that genre
                            artists_list = data['artists']['items']

                            # time to add artists to dictionary
                            for artist in artists_list:

                                #extract data for each artist
                                id = artist['id']
                                name = artist['name']
                                genres = artist['genres']
                                popularity = artist['popularity']

                                #check for membership to avoid duplicate entries
                                if id not in self.artist_data:
                                    self.artist_data[id] = {
                                    'name': name,
                                    'genres': genres,
                                    'popularity': popularity
                                }
                                    #print(f"added artist {name}")

                                if len(self.artist_data) == 100:
                                    print(self.artist_data)

                            #moving onto the next page
                            next_page = data['artists']['next']
                            if next_page is not None:
                                async with session.get(next_page, headers=self.headers) as response:
                                    self.api_call_counter()
                                    if response.status == 429:
                                        retry_after = int(response.headers.get('Retry-After', 5))
                                        print("Rate limit reached")
                                        await asyncio.sleep(retry_after)
                                        continue #TO DO - known issue: this skips the current iteration 
                                    else: data = await response.json()
                            else:
                                break #reached end of artists for that genre/category
                        
                    elif response.status == 429:
                        retry_after = int(response.headers.get('Retry-After', 5))
                        print("Rate limit reached")
                        await asyncio.sleep(retry_after)
                        continue #TO DO - known issue: this skips the current iteration 
                    elif response.status == 401: #token expired
                        print("Expired token...refreshing")
                        self.get_token()
                    else:
                        print(f'Error: {response.status}')
                        raise Exception(f'Error: {response.status}')
                    
                print("total arists in dict:", len(self.artist_data))
                    





        

        

    


    

    



