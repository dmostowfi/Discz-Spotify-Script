# Discz-Spotify-Script

## How to run the script

1. For reference, these are the required libraries I used, in case you need to install or update any of them: base64, requests, os, time, aiohttp, asyncio, deque, load_dotenv
2. Create an .env file in your directory and add your Spotify app credentials:
`CLIENT_ID=your_spotify_client_id`
`CLIENT_SECRET=your_spotify_client_secret`
3. Run the `main.py` file. This will automatically import the `SpoifyScraper` class, which contains all the methods to execute the task, from the `spotify_api.py` file.
4. You will see that the script is running and the `artist_data` dictionary is growing by the messages "# API calls in last 30 seconds: #" and "total arists in dict: #" printed to the console at every iteration. When the first 100 artists are added, the dictionary will print to the console.     

## Summary of the approach

### 1. Extract artist data: 

Given there is no direct route to extract all of Spotify's artist data, I created helper functions that would produce filtering fields to be used when calling Spotify's` /search` API. The following functions are all included in the `SpotifyScraper` class in `spotify_api.py`:

| Method | Purpose | Endpoint | Tradeoffs |
| ------ | -------------------------- | ------ | -------------------------- |
| `get_genres` | Creates a set of 126 genres | /recommendations/ available-genre-seeds | Provides an entry point to getting initial results from `/search`, but is limited to broader genres that may exclude niche artists | 
`get_categories` | Creates a list of 52 categories | /browse/categories | Searching by category aims to retrieve more niche artists not captured in genre filter, though there is likely some overlap; requires more iterations and API calls to page through /categories results|  
`get_niche_genres` | Creates a set of 42 new genres. Loops thru the original list of 126 genres to call` /search`, extract "genres" field for each artist, and add new, more niche genres to the set if not already in original genres set | /search | Searching on more niche genres allows newer artists to appear in `/search`, though this function takes O(n^3) time in the worst case to loop through artists, genres, and then paged `/search` results. (A note on this below) |
`add_artists` | Takes a genres set/category list as an argument and either "genre" or "category" query. Loops through list/set to call `/search` on a `genre` or `category`, then iterates through the returned artists to extract required data (will comment on writing data to dict in next section) | /search | Although params for `/search` are slightly different whether searching on "genre" or "category", wanted to ensure `add_artists` accepted both types of inputs to adhere to "DRY" principle |

"If I had more time" sidenote #1-2: 
* Ideally I would have written more helper functions like the `get_` methods above leveraging different endpoints to extract even more artists.
* Extend `add_artists` with the code for `get_niche_genres`. That is, when iterating through the /search endpoint (filtered by genre) in `add_artists`, extract the genres field at the same time as the artist data, adding genres to `niche_genres_set` only if not in `genres_set`. This eliminates the need to complete the loop twice.   

### 2. Save artist data to dictionary:

* Once the required artist fields are extracted from `/search` in `add_artists`, they are added to a dictionary called `artist_data`. I chose a dictionary data structure because operations for checking membership and insertion are both constant time (O(1)) on average, which is useful given that one artist can be associated with multiple genres/categories, and will likely appear multiple times in the various searches on genres, niche genres, and categories. This also ensured that all artists added to the dictionary were unique. 

"If I had more time" sidenote #3: Writing the results to a MySQL database would have eliminated the need to re-run the long script and enabled easier access once the final results were completed. I would have done this by setting up a database, such as using AWS's Relational Database Service, creating a table called "artist_data" with the 4 required fields, then writing a python script that connects to the database and uses INSERT INTO function to insert the data from `/search`.

### 3. (Trying to) Hit and Handle Spotify's Rate Limit:

#### Hitting the rate limit
Although I never hit the rate limit, I achieved a max of 240 API calls per rolling 30-second window using asynchronous programming. This is detailed in the asynchronous `run_spotify_scraper` method in the `main.py file`, and the flow is as follows:

1. Run `get_genres` and `get_categories` simultaneously
2. Prepare to input the results of `get_genres` and `get_categories` in `add_artists`, and prepare to run `get_niche_genres`
3. Run `get_niche_genres` when `get_genres` and `get_categories` finish
4. Run `add_artists` on results from `get_genres`, `get_categories`, and `get_niche_genres` (which are each lists/sets) simultaneously. 

"If I had more time" sidenote #4-5: 
* Find more endpoints to extract even more artists from `/search`, then run those concurrently within the flow above. Of course, I would do so with an eye for time complexity, ideally trying not to run loops that would exceed linear time. 
* I want to note that I used `aiohttp` to make async HTTP requests. I was running into an SSL certificate error, which may be due to my older macOS. I want to acknowledge that my quick fix (setting `SSL verification = False`) is not best practice, but I went with it in favor of getting the functionality working. If I had more time I would properly update my certificates.  

#### Handling the rate limit
My current approach to handling the rate limit is to wait to hit the `429` status code, extract the `Retry-After` field from the response header, then hold off the script's execution until `Retry-After` time has passed.  

"If I had more time" sidenote #6: The above was the most straightforward approach given the time constraints, but ideally I could have inspected the API's behavior when the rate limit was hit and decided the best course of action from there. A serious drawback to the above approach is being beholden to Spotify's suggestion, which I expect would be padded to moderate API usage. Some other approaches I may have considered (+ potential drawbacks) include: 

*  Getting "just close enough": Once I identified when the rate limit was reached, I could used my `api_call_counter` helper function to track if I was about to hit the limit, approximated the minimum time needed to pause the script's execution to bring down that count, and then continued the script without ever hitting the 429 code. 
* Using multiple tokens: First, this might be considered "cheating", but also the documentation suggests that rate limits are imposed when an APP makes too many calls, so my interpretation is that this wouldn't have solved the issue.
* [Spotipy Python library](https://spotipy.readthedocs.io/en/2.22.1/#): Similarly, I'm not familiar with how trustworthy non-official Python libraries are, though I would have loved to look more into it!  


### 4. Testing

* Used `unittest` Python library to run various unit tests in `testing.py`
* Created a helper function called `api_call_counter` to count the number of API calls in a rolling 30-second period. This function creates a queue data structure that holds the timestamps of every API call. I chose this DS because enqueuing and dequeing both take constant time (O(1)) and the behavior of this data structure is perfect for allowing me to easily remove the oldest element (i.e., the older timestamps when more than 30 seconds have passed)  
* Also manually tested using print statements, such as tracking the results of `api_call_counter` and measuring the final length of `artist_data`.

"If I had more time" sidenote #7: Additional unit tests I would have run include: 
* simulating receiving 429 response code and testing behavior on `get_genres`, `get_categories`, `get_niche_genres`, and `add_artists` (separately and together). I discovered [mockunittest](https://docs.python.org/3/library/unittest.mock.html) on the final day but didn't get to familiarize myself with it
* confirm insertion into `artist_data` dictionary (did so manually instead)
* simulate token expiration (401 code)

## Thank you! 

Thank you for the opportunity to work on this challenge, and special thanks to Emily for your mentorship and collaboration throughout this process. Your partnership was instrumental in making this a fantastic learning experience!





