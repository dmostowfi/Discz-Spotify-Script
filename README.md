# Discz-Spotify-Script

## Summary of the approach

1. Extract artist data: Given there is no direct route to extract all of Spotify's artist data, I created helper functions that would produce fields to be used when calling Spotify's /search API:

| Function | Purpose | Endpoint(s) Used | Tradeoffs |
| -------- | -------------------- | ----------- | -------------------------- |
| get_genres | Creates a set of 126 genres | https://api.spotify.com/v1/recommendations/available-genre-seeds | Provides an entry point to getting initial results from /search, but is limited to broader genres that may exclude niche artists | 
get_categories | Creates a list of 52 categories | https://api.spotify.com/v1/browse/categories | Searching by category aims to retrieve more niche artists not captured in genre filter, though there is likely some overlap; requires more iterations and API calls to page through categories results|  
get_niche_genres | Creates a set of 168 new genres. Loops thru the original list of 126 genres to call /search, extract "genres" field for each artist, and add new, more niche genres to set | https://api.spotify.com/v1/search | Searching on more niche genres allows newer artists to appear in /search, though this function takes O(n^3) time in the worst case to loop through artists, genres, and then paged /search results |
add_artists | Takes a genres set/category list as an argument and either "genre" or "category" query. Loops through list/set to call /search on a genre or category, then iterates through the returned artists to extract required data (will comment on writing data in next section) | https://api.spotify.com/v1/search | Although params for /search are slightly different whether searching on "genre" or "category", wanted to ensure add_artists accepted both types of inputs to adhere to "DRY" principle |   


## How to run the script
TO DO

