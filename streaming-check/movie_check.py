#!/usr/bin/python3

import requests
import urllib
from datetime import datetime
import os
import argparse

def get_args():
    parser = argparse.ArgumentParser(description='Search movie streaming availability.')
    parser.add_argument('--year', type=int, help='Specify movie release year')
    return parser.parse_args()

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

args = get_args()
movie = input("Enter a movie: ")
movie_safe = urllib.parse.quote_plus(movie)

if args.year:
    tmdb_search = requests.get(f"{tmdb_url}/search/movie?language=en-US&query={movie_safe}&page=1&include_adult=false&primary_release_year={args.year}", headers=tmdb_headers).json()
else:
    tmdb_search = requests.get(f"{tmdb_url}/search/movie?language=en-US&query={movie_safe}&page=1&include_adult=false", headers=tmdb_headers).json()

if not tmdb_search["results"]:
    print("I'm having trouble finding that movie. Check your spelling and try again.")
    exit()

movie_id = tmdb_search['results'][0]['id']
movie_tile = tmdb_search['results'][0]['title']
movie_release_check = tmdb_search['results'][0]['release_date']

if movie_release_check:
    movie_release = datetime.strptime(tmdb_search['results'][0]['release_date'], "%Y-%m-%d")
else: movie_release = "???"

movie_rating = tmdb_search['results'][0]['vote_average']

sa_querystring = {"country":"us","tmdb_id":f"movie/{movie_id}","output_language":"en"}
sa_request = requests.request("GET", sa_url, headers=sa_headers, params=sa_querystring)


if sa_request.status_code == 404:
    print("I'm having trouble finding that movie. Check your spelling and try again.")
    exit()

sa_response = sa_request.json()

services = sa_response["streamingInfo"]

def services_speller(service):
    if service == "hbo":
        service_proper = "HBO Max"
    elif service == "hulu":
        service_proper = "Hulu"
    elif service == "prime":
        service_proper = "Amazon Prime"
    elif service == "netflix":
        service_proper = "Netflix"
    elif service == "disney":
        service_proper = "Disney+"
    elif service == "apple":
        service_proper = "Apple TV+"
    elif service == "paramount":
        service_proper = "Paramount+"
    else:
        return service
    return service_proper
    

print(movie_tile + f" ({movie_release.year})")
print(f"Rating: {movie_rating}")
if not services:
    print("Streaming not available :(")
for s in services:
    leaving_epoch = sa_response["streamingInfo"][s]["us"]["leaving"]
    leaving_date = datetime.fromtimestamp(int(leaving_epoch)).strftime('%Y-%m-%d')
    link = sa_response["streamingInfo"][s]["us"]["link"]
    print(f"Available on {services_speller(s)}")
    if leaving_epoch != 0:
        print(f"Will be leaving {s} on {leaving_date}")
    print(f"Watch here: {link}")