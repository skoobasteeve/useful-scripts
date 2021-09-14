#!/usr/bin/python3

"""

This script gets uploaded files from a Netlify Forms submission, renames them, and uploads them to a Nextcloud folder.
I originally used it to download vaccine cards that my wedding guests submitted and move them to a shared folder.

Required Packages:
pip install requests
pip install webdavclient3


"""

import requests
from webdav3.client import Client
import urllib.request
import os
import shutil

### USER VARIABLES ###

# Netlify
USERNAME=""
OAUTH_TOKEN=""
SITE_ID=""
FORM_ID=""

# Nextcloud
NEXTCLOUD_DIR = ""
NEXTCLOUD_USER = ""
NEXTCLOUD_PASS = ""
NEXTCLOUD_URL = ""

#### DON'T EDIT BELOW THIS LINE ####

# Netlify API calls
headers = {'Authorization': 'Bearer ' + OAUTH_TOKEN , 'User-Agent': 'MyApp (' + USERNAME + ')'}
form_submissions = requests.get(f"https://api.netlify.com/api/v1/sites/{SITE_ID}/forms/{FORM_ID}/submissions", headers=headers).json()
vaccine_cards = {}
webdav_options = {
 'webdav_hostname': NEXTCLOUD_URL,
 'webdav_login':    NEXTCLOUD_USER,
 'webdav_password': NEXTCLOUD_PASS
}
client = Client(webdav_options)
nc = client.list(NEXTCLOUD_DIR)
existing_cards = nc[1:]
new_cards = []
all_cards = []

#### FUNCTIONS ####

def build_dict():
    for entry in form_submissions:
        name = entry["data"]["name"]
        card_img = entry["data"]["vaccine_card"]["url"]
        vaccine_cards[name] = card_img

def card_sizes_netlify():
    netlify_cards = {}
    for name, card in vaccine_cards.items():
        response = urllib.request.urlopen(card)
        info = response.headers
        filesize = info['Content-Length']
        extension = "." + str(info.get_content_subtype())
        name_clean = name.strip()
        output_file = name_clean.replace(' ', '_') + extension
        netlify_cards[output_file] = filesize
    return netlify_cards

def card_sizes_nextcloud():
    nextcloud_cards = {}
    for card in existing_cards:
        card_info = client.info(NEXTCLOUD_DIR + card)
        filesize = card_info['size']
        nextcloud_cards[card] = filesize
    return nextcloud_cards

def download_cards():
    print("Downloading cards from Netlify...")
    for name, card in vaccine_cards.items():
        response = urllib.request.urlopen(card)
        info = response.headers
        extension = "." + str(info.get_content_subtype())
        name_clean = name.strip()
        output_file = name_clean.replace(' ', '_') + extension
        all_cards.append(output_file)
        if output_file not in existing_cards:
            new_cards.append(output_file)
            file_download = requests.get(card, stream=True)
            if os.path.exists('tmp/') == False:
                os.makedirs('tmp/')
            print(output_file)
            with open(f'tmp/{output_file}', 'wb') as f:
                for chunk in file_download.iter_content(2000):
                    f.write(chunk)
        else:
            continue
    
def upload_cards():
    num_cards = len(new_cards)
    current_card = 0
    print("")
    print("Uploading cards to Nextcloud...")
    for card in os.listdir("tmp"):
        if card in new_cards:
            current_card += 1
            print(f"Uploading card {current_card} of {num_cards}")
            client.upload_sync(remote_path=f'{NEXTCLOUD_DIR}/{card}', local_path=f"tmp/{card}")
        else:
            continue
    print("Done!")

def main():
    build_dict()
    print("Checking for new vaccine cards...")
    if card_sizes_netlify() != card_sizes_nextcloud():
        download_cards()
    else:
        print("Nothing new to download!")
    if new_cards:
        upload_cards()
    if os.path.exists('tmp/') == True:
        print("")
        print("Cleaning up...")
        shutil.rmtree('tmp/')


if __name__ == '__main__':
    main()
