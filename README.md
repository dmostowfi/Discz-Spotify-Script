# Discz-Spotify-Script

## Summary of the approach

### 1. Extract artist data: 

Given there is no direct route to extract all of Spotify's artist data, I created helper functions that would produce fields to be used when calling Spotify's /search API:

| Function | Purpose | Endpoint(s) Used | Tradeoffs |
| ------ | -------------------------- | ------ | -------------------------- |
| get_genres | Creates a set of 126 genres | https://api.spotify.com/v1/recommendations/available-genre-seeds | Provides an entry point to getting initial results from /search, but is limited to broader genres that may exclude niche artists | 
get_categories | Creates a list of 52 categories | https://api.spotify.com/v1/browse/categories | Searching by category aims to retrieve more niche artists not captured in genre filter, though there is likely some overlap; requires more iterations and API calls to page through categories results|  
get_niche_genres | Creates a set of 168 new genres. Loops thru the original list of 126 genres to call /search, extract "genres" field for each artist, and add new, more niche genres to set | https://api.spotify.com/v1/search | Searching on more niche genres allows newer artists to appear in /search, though this function takes O(n^3) time in the worst case to loop through artists, genres, and then paged /search results |
add_artists | Takes a genres set/category list as an argument and either "genre" or "category" query. Loops through list/set to call /search on a genre or category, then iterates through the returned artists to extract required data (will comment on writing data in next section) | https://api.spotify.com/v1/search | Although params for /search are slightly different whether searching on "genre" or "category", wanted to ensure add_artists accepted both types of inputs to adhere to "DRY" principle |

"If I had more time" sidenote #1: Ideally I would have written more helper functions like the "get_" methods above leveraging different endpoints to extract even more artists. 

### 2. Save artist data to dictionary:

* Once the required artist fields are extracted from /search in add_artists, they are added to a dictionary called 'artist_data.' I chose a dictionary data structure because operations for checking membership and insertion are both constant time (O(1)) on average, which is useful given that one artist can be associated with multiple genres/categories, and will likely appear multiple times in the various searches on genres, niche_genres, and categories. This also ensured that all artists added to the dictionary were unique. 

"If I had more time" sidenote #2: Writing the results to a MySQL database would have eliminated the need to re-run the long script and enabled easier access once the final results were completed. I would have done this by setting up a database, such as using AWS's Relational Database Service, creating a table called "artist data" with the 4 required fields, then writing a python script that connects to the database and uses INSERT INTO function to insert the data from /search.  

### 5. Testing

* Used unittest Python library to run various unit tests in testing.py
* Also manually tested through api_call_counter, a method for counting number of API calls in a 30-second period, and print statements, such as measuring the final length of artist_data.   

## How to run the script
TO DO

