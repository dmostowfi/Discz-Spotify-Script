# Discz-Spotify-Script

## Summary of the approach

1. Extract artist data: Given there is no direct route to extract all of Spotify's artist data, I created helper functions that would produce fields to be used when calling Spotify's /search API:

| Function | Purpose | Endpoint(s) Used | Tradeoffs |
| -------- | -------------------- | ----------- | -------------------------- |
| get_genres | Extracts a list 126 of genres | https://api.spotify.com/v1/recommendations/available-genre-seeds | Provides an entry point to getting initial results from /search, but is limited to broader genres that may exclude niche artists | get_categories | Extracts a list of 52 categories | https://api.spotify.com/v1/browse/categories | Searching by category aims to retrieve more niche artists not captured in genre filter, though there is likely some overlap; requires more iterations and API calls to page through categories results|  


## How to run the script
TO DO

