import os
import requests
from dotenv import load_dotenv
from datetime import date, datetime, time, timedelta
import RPi.GPIO as GPIO
from PCF8574.lcd import LCD
from PCF8574.pcf8574 import PCF8574
import busio
import board

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

# GPIO pins of the buttons
S1 = 4
S2 = 16
S3 = 10
S4 = 9
inputs = [S1, S2, S3, S4]
GPIO.setmode(GPIO.BCM)

# setting up buttons as inputs
for switch in inputs:
    GPIO.setup(switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# set up lcd
lcd = LCD(PCF8574(busio.I2C(board.SCL, board.SDA), 0x27), num_rows=4, num_cols=20)

column = 0


def checkSwitches():
    # Check status of all four switches on the LCD board
    val1 = not GPIO.input(S1)
    val2 = not GPIO.input(S2)
    val3 = not GPIO.input(S3)
    val4 = not GPIO.input(S4)

    if val1 == GPIO.HIGH:
        return "S1"
    elif val2 == GPIO.HIGH:
        return "S2"
    elif val3 == GPIO.HIGH:
        return "S3"
    elif val4 == GPIO.HIGH:
        return "S4"
    return "0"


def summarize_distance_in_list(activities):
    summarized_distance = 0

    for activity in activities:
        summarized_distance += activity['distance']

    return summarized_distance


def get_alltime_distance():
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


try:
    lcd.print(str(get_alltime_distance() / 1000) + ' Km')

except KeyboardInterrupt:
    lcd.clear()
    GPIO.cleanup()
