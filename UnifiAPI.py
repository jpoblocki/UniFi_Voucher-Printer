import requests
import json
from datetime import datetime, timedelta, timezone
import pytz
import urllib3

from Print import printVoucher


# Set Variables
# ---------------------------------------------
base_url = "https://unifi.***.com"
site_name = "default"
voucher_old_delete_days = 7
username = "api_hotspot"
password = "***"

logo_file = "***.png"
network_name = "ssid-name"
network_password = "ssid-password"


# Set Constants
# ---------------------------------------------
auth_url = f"{base_url}/api/login"
voucher_cmd_url = f"{base_url}/api/s/{site_name}/cmd/hotspot"
voucher_list_url = f"{base_url}/api/s/{site_name}/stat/voucher"
eastern_time_zone = pytz.timezone("America/New_York")

default_headers = {
    "Content-Type": "application/json"
}

urllib3.disable_warnings()

def pastTime():
    days_ago_eastern = datetime.now(tz=timezone.utc) - timedelta(days=voucher_old_delete_days)
    days_ago_eastern = days_ago_eastern.astimezone(eastern_time_zone)
    return days_ago_eastern

def expNote():
    days_until_eastern = datetime.now(tz=timezone.utc) + timedelta(days=voucher_old_delete_days)
    days_until_eastern = days_until_eastern.astimezone(eastern_time_zone)
    days_until_eastern = days_until_eastern.strftime('%m/%d/%Y')
    expiration_note = f"If unused, this voucher will expire on {days_until_eastern}"
    return expiration_note

session = requests.Session()


def createVoucher():
    # Authentication
    # ---------------------------------------------
    auth_body = {
        "for_hotspot": True,
        "site_name": site_name,
        "username": username,
        "password": password
    }

    auth_response = session.post(auth_url, headers=default_headers, data=json.dumps(auth_body), verify=False)
    auth_response.raise_for_status()

    # Create Voucher
    # ----------------------------------------------
    voucher_create_body = {
        "quota": 0,
        "note": f"VP - {datetime.now().strftime('%m/%d/%Y %I:%M:%S %p')}",
        "n": 1,
        "expire_number": 24,
        "expire_unit": 60,
        "cmd": "create-voucher"
    }

    voucher_create_response = session.post(voucher_cmd_url, headers=default_headers, data=json.dumps(voucher_create_body), verify=False)
    voucher_create_response.raise_for_status()
    voucher_created = voucher_create_response.json().get('data')

    # List All Vouchers
    # ------------------------------------------------
    voucher_list_response = session.get(voucher_list_url, verify=False)
    voucher_list_response.raise_for_status()
    voucher_list = voucher_list_response.json().get('data')

    # Find newly created voucher in All Vouchers
    # -------------------------------------------------
    created_voucher = next((v for v in voucher_list if v['create_time'] == voucher_created[0]['create_time']), None)

    if created_voucher:
        voucher_code = created_voucher['code'][:5] + '-' + created_voucher['code'][5:]
        voucher_note = created_voucher['note']
        print(voucher_note)
        print(voucher_code)

    expiration_note = expNote()

    printVoucher(logo_file, network_name, network_password, voucher_code, voucher_note, expiration_note)
    
    return voucher_list


# Remove Voucher Function
# -------------------------------------------------
def remove_vouchers(voucher_list):
    if not voucher_list:
        return

    vouchers_to_delete = [v['_id'] for v in voucher_list]

    if vouchers_to_delete:
        voucher_delete_body = {
            "ids": vouchers_to_delete,
            "cmd": "delete-vouchers"
        }

        voucher_delete_response = session.post(voucher_cmd_url, headers=default_headers, data=json.dumps(voucher_delete_body), verify=False)
        voucher_delete_response.raise_for_status()


# Remove Expired Vouchers
# ---------------------------------------------------------
def remove_expired_vouchers():
    expired_vouchers = [v for v in voucher_list if v['status'] == "EXPIRED"]
    #print(expired_vouchers)
    remove_vouchers(expired_vouchers)


# Remove Old Vouchers
# ----------------------------------------------------------
def remove_old_vouchers():
    days_ago_eastern = pastTime()

    old_vouchers = []

    for voucher in voucher_list:
        utc_datetime = datetime.fromtimestamp(voucher['create_time'], tz=timezone.utc)
        eastern_datetime = utc_datetime.astimezone(eastern_time_zone)
        if eastern_datetime < days_ago_eastern and voucher['note'].startswith("VP"):
            old_vouchers.append(voucher)

    remove_vouchers(old_vouchers)
    

# Run on button press
# -----------------------------------------------------------
from gpiozero import Button,LED
from time import sleep
import threading

button = Button(17)
led = LED(18)

led.on()

blinking = False

def blink_led():
    while blinking:
        led.on()
        sleep(.25)
        led.off()
        sleep(.25)
        
def start_blinking():
    global blinking
    blinking = True
    thread = threading.Thread(target=blink_led)
    thread.start()
    
def stop_blinking():
    global blinking
    blinking = False
    sleep(.5)
    led.on()
    

x = 0


while True:
    if button.is_pressed:
        start_blinking()
        
        x = x + 1
        print(f"PRESSED - {x}")
        
        voucher_list = createVoucher()
        
        remove_expired_vouchers()
        remove_old_vouchers()
        
        stop_blinking()
        
        button.wait_for_release()