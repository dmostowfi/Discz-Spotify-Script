import base64
import requests

#class for all interactions with Spotify API
class SpotifyAPI:
    
    # method for getting an access token
    def get_token(self):
    
        # get spotify app credentials
        client_id = '498bd1724a06480b9564f268488c2e68'
        client_secret = '0d249f3ca810421e8bf969bbcae7290b'

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

        # parse response
        if response.status_code == 200:
            self.token = response.json()['access_token']
            print(f"Access token: {self.token}")

            #update the header to include the token for future API requests
            self.headers = {
                'Authorization': f'Bearer {self.token}'}

        else:
            print(f"Failed to get token: {response.content}")

    

    # method for calling genres API
    def get_genres(self):
        response = requests.get('https://api.spotify.com/v1/recommendations/available-genre-seeds', headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            self.genres_list = data['genres']
        else:
            print(f'Error: {response.content}')


    #TO DO: try to hit the rate limit
    #TO DO: potentially write to DB
    #method for writing artist data to dictionary
    def add_artists(self):

        # initialize empty dict
        artist_data = {}

        url = "https://api.spotify.com/v1/search"

        for genre in self.genres_list[:3]: #TO DO: REMOVE INDEX. FOR TESTING ONLY
            
            # first, call Spotify /search API and filter on genre
            params = {
                f"q": "genre:\{genre}\"",
                "type": "artist"
            }
            response = requests.get(url, headers=self.headers, params=params)


            # then, get artist data 
                #TO DO: think about how to use this to improve efficiency``
                #newurl = data['artists']['href']
            if response.status_code == 200:
                data = response.json()
                
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
                
            else:
                # TO DO: what happens when token expires
                # TO DO: throw error  
                print(f'Error: {response.status_code}')






        

        

    


    

    



