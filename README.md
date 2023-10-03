# Discz-Spotify-Script

## How to run the script

1. Ensure all required libraries are properly installed.
2. Create an .env file in your directory and add your Spotify app credentials:
`CLIENT_ID=your_spotify_client_id`
`CLIENT_SECRET=your_spotify_client_secret`
3. Run the `main.py` file. This will automatically import the `SpoifyScraper` class, which contains all the methods to execute the task, from the `spotify_api.py` file.
4. Logs printed to the console will indicate that the script is running.    

## Summary of the approach

### 1. Extract artist data: 

Given there is no direct route to extract all of Spotify's artist data, I created helper functions that would produce fields to be used when calling Spotify's` /search` API. The following functions are all included in the `SpotifyScraper` class in `spotify_api.py`:

| Method | Purpose | Endpoint(s) | Tradeoffs |
| ------ | -------------------------- | ------ | -------------------------- |
| `get_genres` | Creates a set of 126 genres | /recommendations/ available-genre-seeds | Provides an entry point to getting initial results from `/search`, but is limited to broader genres that may exclude niche artists | 
`get_categories` | Creates a list of 52 categories | /browse/categories | Searching by category aims to retrieve more niche artists not captured in genre filter, though there is likely some overlap; requires more iterations and API calls to page through categories results|  
`get_niche_genres` | Creates a set of 168 new genres. Loops thru the original list of 126 genres to call` /search`, extract "genres" field for each artist, and add new, more niche genres to the set | /search | Searching on more niche genres allows newer artists to appear in `/search`, though this function takes O(n^3) time in the worst case to loop through artists, genres, and then paged `/search` results |
`add_artists` | Takes a genres set/category list as an argument and either "genre" or "category" query. Loops through list/set to call `/search` on a `genre` or `category`, then iterates through the returned artists to extract required data (will comment on writing data in next section) | /search | Although params for `/search` are slightly different whether searching on "genre" or "category", wanted to ensure `add_artists` accepted both types of inputs to adhere to "DRY" principle |

"If I had more time" sidenote #1: Ideally I would have written more helper functions like the `get_` methods above leveraging different endpoints to extract even more artists. 

### 2. Save artist data to dictionary:

* Once the required artist fields are extracted from `/search` in add_artists, they are added to a dictionary called `artist_data`. I chose a dictionary data structure because operations for checking membership and insertion are both constant time (O(1)) on average, which is useful given that one artist can be associated with multiple genres/categories, and will likely appear multiple times in the various searches on genres, niche genres, and categories. This also ensured that all artists added to the dictionary were unique. 

"If I had more time" sidenote #2: Writing the results to a MySQL database would have eliminated the need to re-run the long script and enabled easier access once the final results were completed. I would have done this by setting up a database, such as using AWS's Relational Database Service, creating a table called "artist data" with the 4 required fields, then writing a python script that connects to the database and uses INSERT INTO function to insert the data from `/search`.

### 3. (Trying to) Hit and Handle Spotify's Rate Limit:

#### Hitting the rate limit
Although I never hit the rate limit, I achieved a max of 240 API calls per rolling 30-second window using asynchronous programming. This is detailed in the asynchronous `run_spotify_scraper` method in the `main.py file`, and the flow is as flows:

1. Run `get_genres` and `get_categories` simultaneously
2. Prepare to input the results of `get_genres` and `get_categories` in `add_artists`, and prepare to run `get_niche_genres`
3. Run `get_niche_genres` when `get_genres` and `get_categories` finish
4. Run `add_artists` on results of `get_genres`, `get_categories`, and `get_niche_genres` simultaneously. 

"If I had more time" sidenote #3: Find more endpoints to extract even more artists from `/search`, then run those concurrently within the flow above. Of course, I would do so with an eye for time complexity, ideally trying not to exceed loops that would exceed linear time. 

#### Handling the rate limit
My current approach to handling the rate limit is to wait to hit the `429` status code, extract the `Retry-After` field from the response header, then hold off the script's execution until `Retry-After` time has passed.  

"If I had more time" sidenote #4: The above was the most straightforward approach given the time constraints, but ideally I could have inspected the API's behavior when the rate limit was hit and decided the best course of action from there. A serious drawback to the above solution is being beholden to Spotify's suggestion, which is expected to be longer to moderate API usage. Some other approaches I may have considered (+ potential drawbacks) include: 

*  Getting "just close enough": Once I identified when the rate limit was reached, I could used my `api_call_counter` helper function to track if I was about to hit the limit, approximated the minimum time needed to pause the script's execution to bring down that number, and then continued the script without ever hitting the 429 code. 
* Using multiple tokens: First, this might be considered "cheating", but also the documentation suggests that rate limits are imposed when an APP makes too many calls, so my interpretation is that this wouldn't have solved the issue.
* [Spotipy Python library](https://spotipy.readthedocs.io/en/2.22.1/#): Similarly, I'm not familiar with how trustworthy non-official Python libraries are, though I would have loved to look more into it!  


### 4. Testing

* Used unittest Python library to run various unit tests in testing.py
* Created a helper function called api_call_counter to count the number of API calls in a rolling 30-second period. 
* Also manually tested using print statements, such as tracking the results of api_call_counter and measuring the final length of artist_data.

"If I had more time" sidenote #5: Additional unit tests I would have run include: 
* simulating receiving 429 response code and testing behavior on `get_genres`, `get_categories`, `get_niche_genres`, and `add_artists` (separately and together)
* confirm insertion into `artist_data` dictionary (did so manually instead)
* simulate token expiration 

## Thank you! 

Thank you for the opportunity to work on this challenge, and special thanks to Emily for your mentorship and collaboration throughout this process. Your partnership was just what I needed to continue making progress!   





