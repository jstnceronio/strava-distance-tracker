import os
import requests
from dotenv import load_dotenv
from datetime import date, datetime, time, timedelta

load_dotenv()

auth_url = "https://www.strava.com/oauth/token"
activities_url = "https://www.strava.com/api/v3/athlete/activities"
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

def summarize_distance_in_list(activities):
    summarized_distance = 0

    for activity in activities:
        summarized_distance += activity['distance']

    return summarized_distance


def get_all_distance():
    page = 1
    page_not_empty = True
    overall_distance = 0
    activity_pages = []
    header = {'Authorization': 'Bearer ' + access_token}

    while page_not_empty:
        param = {'per_page': 200, 'page': page}
        activity_page = requests.get(activities_url, headers=header, params=param).json()
        activity_pages.append(activity_page)
        page_not_empty = bool(activity_page)
        page += 1

    for page in activity_pages:
        overall_distance += summarize_distance_in_list(page)

    return overall_distance


def get_weekly_distance():
    if date.today().weekday() == 0:
        last_monday = round(datetime.combine(date.today(), time.min).timestamp())
    else:
        last_monday = round(
            datetime.combine(
                date.today() - timedelta(days=date.today().weekday()), time.min
            ).timestamp()
        )

    header = {'Authorization': 'Bearer ' + access_token}
    param = {'after': last_monday, 'per_page': 200, 'page': 1}  # todo: add weekly parameter

    activities = requests.get(activities_url, headers=header, params=param).json()

    return summarize_distance_in_list(activities)


def main():
    print(get_weekly_distance())


if __name__ == "__main__":
    main()
