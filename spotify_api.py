import base64
import requests
import os
import time
import aiohttp
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
        self.total_api_calls = 0
        self.timestamps = deque() #for counting #API calls in 30sec
    
    # method for retrieving an access token from Spotify
    def _access_token(self):
    
        # get spotify app credentials
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")

        # encoding the credentials
        auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode('utf-8')).decode('utf-8')

        # documentation for client creds flow: https://developer.spotify.com/documentation/web-api/tutorials/client-credentials-flow
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
        self.total_api_calls += 1

        # parse response
        if response.status_code == 200:
            self.token = response.json()['access_token']
            print(f"Access token: {self.token}")

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
            #sync approach: #response = requests.get('https://api.spotify.com/v1/recommendations/available-genre-seeds', headers=self.headers)
                self.api_call_counter()
                self.total_api_calls += 1
                if response.status == 200:
                    data = await response.json()
                    self.genres_list = data['genres']
                    print(self.genres_list)
                    print("# genres = ",len(self.genres_list))
                else:
                    error_msg = await response.content
                    print(f'Error: {error_msg}')
                    raise Exception("Failed to get genres")
        
    # method for getting markets where Spotify is available
    def get_markets(self):
        response = requests.get('https://api.spotify.com/v1/markets', headers=self.headers)
        self.api_call_counter()
        self.total_api_calls += 1
        if response.status_code == 200:
            data = response.json()
            self.markets_list = data['markets']
            print(self.markets_list)
            print("# markets = ",len(self.markets_list))
        else:
            print(f'Error: {response.content}')
            raise Exception("Failed to get markets")
        
    # method for getting categories
    async def get_categories(self):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            self.categories_list = set() 
            params = {"limit": 50}
            async with session.get('https://api.spotify.com/v1/browse/categories', headers=self.headers, params=params) as response:
            #response = requests.get('https://api.spotify.com/v1/browse/categories', headers=self.headers, params=params)
                self.api_call_counter()
                self.total_api_calls += 1
                if response.status == 200:
                    data = await response.json()
                    while True:
                        categories_json = data['categories']['items']
                        for item in categories_json:
                            category = item['name']
                            self.categories_list.add(category)
                            print("adding to set:", category)

                        #moving onto the next page
                        next_page = data['categories']['next']
                        if next_page is not None:
                            async with session.get(next_page, headers=self.headers, params=params) as response:
                            #response = requests.get(next_page, headers=self.headers)
                                self.api_call_counter()
                                self.total_api_calls += 1
                                if response.status == 429:
                                    print("Rate limit reached")
                                    return
                                else: data = await response.json()
                        else:
                            break #reached end of categories

                    print(self.categories_list)
                    print("# categories = ",len(self.categories_list))
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


    #TO DO: try to hit the rate limit
    #TO DO: potentially write to DB
    #method for writing artist data to dictionary
    def add_artists(self):

        # initialize empty dict
        artist_data = {}

        url = "https://api.spotify.com/v1/search"
        i = 0 #for tracking how many genres we get through before hitting limit
        total_api_calls = 0

        for genre in self.genres_list:
            
            print(f"Finding artists for {genre} genre")
            i += 1
            print("genre_i=", i)
            # first, call Spotify /search API and filter on genre
            params = {
                "q": f"genre:\"{genre}\"",
                "type": "artist", 
                "limit":50
            }
            response = requests.get(url, headers=self.headers, params=params)
            self.api_call_counter()
            self.total_api_calls += 1


            # then, get artist data 
                #TO DO: think about how to use this to improve efficiency``
                #newurl = data['artists']['href']
            if response.status_code == 200:
                data = response.json()

                while True:
                    #list of artists for that genre
                    artists_list = data['artists']['items']
                    print('total items =', data['artists']['total'])

                    # time to add artists to dictionary
                    for artist in artists_list:

                        #extract data for each artist
                        id = artist['id']
                        name = artist['name']
                        genres = artist['genres']
                        popularity = artist['popularity']

                        #check for membership to avoid duplicate entries
                        if id not in artist_data:
                            artist_data[id] = {
                            'name': name,
                            'genres': genres,
                            'popularity': popularity
                        }
                            print(f"added artist {name}")

                    #moving onto the next page
                    next_page = data['artists']['next']
                    if next_page is not None:
                        response = requests.get(next_page, headers=self.headers)
                        self.api_call_counter()
                        total_api_calls += 1
                        if response.status_code == 429:
                            print("Rate limit reached")
                            return
                        else: data = response.json()
                    else:
                        break #reached end of artists for that genre
                
            elif response.status_code == 429:
                print("Rate limit reached")
                return
            else:
                # TO DO: what happens when token expires
                print(f'Error: {response.status_code}')
                raise Exception(f'Error: {response.status_code}')
        print("Total api calls:", total_api_calls)



#uncomment the below for quick testing
#open class:
#spotify = SpotifyAPI()
#spotify.get_token()
#spotify.get_genres()
#spotify.add_artists()





        

        

    


    

    



