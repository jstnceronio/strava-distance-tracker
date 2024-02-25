import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

auth_url = "https://www.strava.com/oauth/token"
activites_url = "https://www.strava.com/api/v3/athlete/activities"

payload = {
    'client_id': os.getenv('CLIENT_ID'),
    'client_secret': os.getenv('CLIENT_SECRET'),
    'refresh_token': os.getenv('REFRESH_TOKEN'),
    'grant_type': "refresh_token",
    'f': 'json'
}

print("Requesting Token...\n")
res = requests.post(auth_url, data=payload, verify=False)
access_token = res.json()['access_token']
print("Access Token = {}\n".format(access_token))

print("Requesting pages (200 activities per full page)...")
page = 1
page_non_empty = True
while page_non_empty:
    header = {'Authorization': 'Bearer ' + access_token}
    param = {'per_page': 200, 'page': page}
    my_activities = requests.get(activites_url, headers=header, params=param).json()
    page_non_empty = bool(my_activities)
    print(page)
    page += 1

print("\n", "activities downloaded")

