from decouple import config
from treasure.models import MapRoom
import requests
import time
import sys
import re
import json

url = config('API_URL')
key = config('API_KEY')



def init_player():
    # while True:
    try:
        player_req = requests.get(
            f"{url}/api/adv/init/",
            headers={
                "Authorization": f"Token {key}"
            }
        )
        player_req.raise_for_status()
        player = player_req.json()
        cooldown = player['cooldown']
        time.sleep(cooldown)
        return player

    except requests.exceptions.RequestException as exception:
        # cooldown -> will have to check response object to test
        if exception.response.status_code == 400:
            time.sleep(cooldown)
        else:
            print(exception)
            sys.exit(1)

def init_move(direction): # only used when resuming from previous cancellation
    try:
        room_req = requests.post(
            f"{url}/api/adv/move/",
            headers={
                "Authorization": f"Token {key}",
                "Content-Type": "application/json"
            },
            data=json.dumps({"direction": f"{direction}"})
        )
        room_req.raise_for_status()
        room = room_req.json()
        print(room["messages"])
        cooldown = room["cooldown"]
        time.sleep(cooldown)
        return room
    except requests.exceptions.RequestException as exception:
        # cooldown -> will have to check response object to test
        if exception.response.status_code == 400:
            time.sleep(cooldown)
        else:
            print(exception)
            sys.exit(1)

def move_player(direction, cur_room_id):
    cur_room = MapRoom.objects.get(room_id=cur_room_id)
    neighbors = json.loads(MapRoom.objects.get(room_id=cur_room_id).neighbors)

    if neighbors[direction] == "?":
        try:
            room_req = requests.post(
                f"{url}/api/adv/move/",
                headers={
                    "Authorization": f"Token {key}",
                    "Content-Type": "application/json"
                },
                data=json.dumps({"direction": f"{direction}"})
            )
            room_req.raise_for_status()
            room = room_req.json()
            print(room["messages"])
            cooldown = room["cooldown"]
            time.sleep(cooldown)
            return room
        except requests.exceptions.RequestException as exception:
            # cooldown -> will have to check response object to test
            if exception.response.status_code == 400:
                time.sleep(cooldown)
            else:
                print(exception)
                sys.exit(1)
    else:
        try:
            room_req = requests.post(
                f"{url}/api/adv/move/",
                headers={
                    "Authorization": f"Token {key}",
                    "Content-Type": "application/json"
                },
                data=json.dumps({
                    "direction": f"{direction}",
                    "next_room_id": f"{neighbors[direction]}"
                })
            )
            room_req.raise_for_status()
            room = room_req.json()
            cooldown = room["cooldown"]
            print("room response: ", room)
            # parse room["messages"] for treasure
            # if treasure -> check inventory
            # if room in inventory -> pick up and continue on
            # if not inventory -> do not pick up
            print(room["messages"])
            time.sleep(cooldown)
            return room
        except requests.exceptions.RequestException as exception:
            # cooldown -> will have to check response object to test
            if exception.response.status_code == 400:
                time.sleep(cooldown)
            else:
                print(exception)
                sys.exit(1)

def take_item(item):
    try:
        item = requests.post(
            f'{url}/api/adv/take/',
            headers={
                'Authorization': f'Token {key}',
                'Content-Type': 'application/json'
            },
            data={
                'name': f'{item}'
            }
        )
        return item
    # if cooldown applies, add exception and while loop
    except requests.exceptions.RequestExceptions as exception:
        print(exception)
        sys.exit(1)

def drop_item(item):
    try:
        item = requests.post(
            f'{url}/api/adv/drop/',
            headers={
                'Authorization': f'Token {key}',
                'Content-Type': 'application/json'
            },
            data={
                'name': f'{item}'
            }
        )
        return item
    # if cooldown applies, add exception and while loop
    except requests.exceptions.RequestExceptions as exception:
        print(exception)
        sys.exit(1)

def sell_treasure():
    while True:
        try:
            sale = requests.post(
                f'{url}/api/adv/sell/',
                headers={
                    'Authorization': f'Token {key}',
                    'Content-Type': 'application/json'
                },
                data={
                    'name': 'treasure'
                }
            )
            message = sale['messages']
            cooldown = sale['cooldown']
            time.sleep(cooldown)
            # returns a message and requires confirmation to sell
            edited_message = re.sub('\([^)]*\)', '(choose YES or NO.)', message)
            print(edited_message)
            prompt = input().lower().strip()
            if prompt == 'yes' or prompt == 'y':
                # make call to confirm
                return confirm_treasure()
            elif prompt == 'no' or prompt == 'n':
                # print confirmation message and return
                # need to decide how to handle return within algorithm
                print("Sale declined.")
                return
        # if cooldown applies, add exception and while loop
        except requests.exceptions.RequestException as exception:
            print(exception)
            sys.exit(1)

def confirm_treasure():
    try:
        confirm = requests.post(
            f'{url}/api/adv/sell/',
            headers={
                'Authorization': f'Token {key}',
                'Content-Type': 'application/json'
            },
            data={
                'name': 'treasure',
                'confirm': 'yes'
            }
        )
        cooldown = confirm['cooldown']
        time.sleep(cooldown)
        return confirm
    except requests.exceptions.RequestException as exception:
        print(exception)
        sys.exit(1)

def check_status():
    try:
        status = requests.post(
            f'{url}/api/adv/status/',
            headers={
                'Authorization': f'Token {key}',
                'Content-Type': 'application/json'
            }
        )
        cooldown = status['cooldown']
        time.sleep(cooldown)
        return status
    # if cooldown applies, add exception and while loop
    except requests.exceptions.RequestException as exception:
        print(exception)
        sys.exit(1)

def change_name(name):
    try:
        name = requests.post(
            f'{url}/adv/change_name/',
            headers={
                'Authorization': f'Token {key}',
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                "name": f"{name}"
            })
        )
        cooldown = name['cooldown']
        time.sleep(cooldown)
        return name
    # if cooldown applies, add exception and while loop
    except requests.exceptions.RequestException as exception:
        print(exception)
        sys.exit(1)

def mine_coin(proof):
    try:
        proof_req = requests.post(
            f'{url}/api/bc/mine/',
            headers={
                'Authorization': f'Token {key}',
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                "name": f"{proof}"
            })
        )
        proof = proof_req.json()
        cooldown = proof['cooldown']
        time.sleep(cooldown)
        return proof
    # if cooldown applies, add exception and while loop
    except requests.exceptions.RequestException as exception:
        print(exception)
        sys.exit(1)
