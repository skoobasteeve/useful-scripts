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
existing_cards = client.list(NEXTCLOUD_DIR)
new_cards = []
all_cards = []

#### FUNCTIONS ####

# Creates a dictionary from the Netlify form data { "Name": "<file_url>" }
def build_dict():
    for entry in form_submissions:
        name = entry["data"]["name"]
        card_img = entry["data"]["vaccine_card"]["url"]
        vaccine_cards[name] = card_img

# Downloads files from Netlify based on their URL and renames the files as "First_Last.jpg(png, pdf, etc)"
def download_cards():
    print("Downloading cards from Netlify...")
    for name, card in vaccine_cards.items():
        response = urllib.request.urlopen(card)
        info = response.info()
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

# Uploads files to the specified Nextcloud/WebDAV folder if they don't already exist
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
    if len(vaccine_cards) > (len(existing_cards) - 1):
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
