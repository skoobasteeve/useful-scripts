#!/usr/bin/python3

import requests
import urllib
from datetime import datetime
import os

tmdb_api_token = os.environ.get("TMDB_API_TOKEN")
sa_api_token = os.environ.get("SA_API_TOKEN")

tmdb_url = "https://api.themoviedb.org/3"
tmdb_headers = {
    'Authorization': f'Bearer {tmdb_api_token}',
    'Content-Type': 'application/json;charset=utf-8',
    'Accept': 'application/json;charset=utf-8'
}

sa_url = "https://streaming-availability.p.rapidapi.com/get/basic"
sa_headers = {
    'x-rapidapi-host': "streaming-availability.p.rapidapi.com",
    'x-rapidapi-key': sa_api_token
    }

movie = "eternals"
movie_safe = urllib.parse.quote_plus(movie)

tmdb_search = requests.get(f"{tmdb_url}/search/movie?language=en-US&query={movie_safe}&page=1&include_adult=false", headers=tmdb_headers).json()

if not tmdb_search["results"]:
    print("I'm having trouble finding that movie. Check your spelling and try again.")
    exit()

movie_id = tmdb_search['results'][0]['id']
movie_tile = tmdb_search['results'][0]['title']
movie_release = datetime.strptime(tmdb_search['results'][0]['release_date'], "%Y-%m-%d")
movie_rating = tmdb_search['results'][0]['vote_average']


sa_querystring = {"country":"us","tmdb_id":f"movie/{movie_id}","output_language":"en"}
sa_response = requests.request("GET", sa_url, headers=sa_headers, params=sa_querystring).json()

services = sa_response["streamingInfo"]

def services_speller(service):
    if service == "hbo":
        service_proper = "HBO Max"
    if service == "hulu":
        service_proper = "Hulu"
    if service == "prime":
        service_proper = "Amazon Prime"
    if service == "netflix":
        service_proper = "Netflix"
    if service == "disney":
        service_proper = "Disney+"
    if service == "apple":
        service_proper = "Apple TV+"
    return service_proper
    
    

print(movie_tile + f" ({movie_release.year})")
print(f"Rating: {movie_rating}")
if not services:
    print("Movie not available for streaming :(")
for s in services:
    countries = sa_response["streamingInfo"][s]
    for c in countries:
        leaving_epoch = sa_response["streamingInfo"][s][c]["leaving"]
        leaving_date = datetime.fromtimestamp(int(leaving_epoch)).strftime('%Y-%m-%d')
        link = sa_response["streamingInfo"][s][c]["link"]
        print(f"Available on {services_speller(s)}")
        if leaving_epoch != 0:
            print(f"Will be leaving {s} on {leaving_date}")
        print(f"Watch here: {link}")