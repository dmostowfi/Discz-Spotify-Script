import base64
import requests

# spotify app credentials
client_id = '498bd1724a06480b9564f268488c2e68'
client_secret = '0d249f3ca810421e8bf969bbcae7290b'

# encode credentials
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

# request token
response = requests.post(
    authOptions['url'],
    headers=authOptions['headers'],
    data=authOptions['data']
)

# parse response
if response.status_code == 200:
    token = response.json()['access_token']
    print(f"Access token: {token}")
else:
    print(f"Failed to get token: {response.content}")


# testing an API request
headers = {
    'Authorization': f'Bearer {token}'
}

response = requests.get('https://api.spotify.com/v1/recommendations/available-genre-seeds', headers=headers)


if response.status_code == 200:
    data = response.json()
    print(data)
else:
    # TO DO: what happens when token expires 
    print(f'Error: {response.status_code}')

