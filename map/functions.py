from decouple import config
from treasure.models import MapRoom
import requests
import time
import sys
import re
import json

url = config("API_URL")
key = config("API_KEY")


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
        cooldown = player["cooldown"]
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
            data=json.dumps({
                "direction": f"{direction}"
            })
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
                data=json.dumps({
                    "direction": f"{direction}"
                })
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
            time.sleep(cooldown)
            print("room response: ", room)
            # parse room["messages"] for treasure
            for item in room["items"]:
                i = str(item)
                print("item: ", item)
                treasure = re.search("treasure", i)
                if treasure:
                    e = examine_item(item)
                    status = check_status()
                    print(e)
                    # print("exiting!")
                    # sys.exit(1)
                    # TODO: will need to check based on large
                    if status["strength"] - status["encumbrance"] > e["weight"]:
                        print(f"{item} item picked up")
                        take_item(item)
                    else:
                        continue 
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
        item_req = requests.post(
            f"{url}/api/adv/take/",
            headers={
                "Authorization": f"Token {key}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "name": f"{item}"
            })
        )
        item_req.raise_for_status()
        i = item_req.json()
        cooldown = i["cooldown"]
        time.sleep(cooldown)
        return i
    # if cooldown applies, add exception and while loop
    except requests.exceptions.RequestExceptions as exception:
        print(exception)
        sys.exit(1)

def drop_item(item):
    try:
        drop_req = requests.post(
            f"{url}/api/adv/drop/",
            headers={
                "Authorization": f"Token {key}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "name": f"{item}"
            })
        )
        drop_req.raise_for_status()
        drop = drop_req.json()
        return drop
    # if cooldown applies, add exception and while loop
    except requests.exceptions.RequestExceptions as exception:
        print(exception)
        sys.exit(1)

def sell_item(item):
    try:
        sell_req = requests.post(
            f"{url}/api/adv/sell/",
            headers={
                "Authorization": f"Token {key}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "name": f"{item}",
                "confirm": "yes"
            })
        )
        sell_req.raise_for_status()
        sell = sell_req.json()
        message = sell["messages"]
        cooldown = sell["cooldown"]
        time.sleep(cooldown)
        return sell
    except requests.exceptions.RequestException as exception:
        print(exception)
        sys.exit(1)

def sell_all_items():
    status = check_status()
    for item in status["inventory"]:
        print(item)
        sell_item(item)

def check_status():
    try:
        status_req = requests.post(
            f"{url}/api/adv/status/",
            headers={
                "Authorization": f"Token {key}",
                "Content-Type": "application/json"
            }
        )
        status_req.raise_for_status()
        status = status_req.json()
        cooldown = status["cooldown"]
        time.sleep(cooldown)
        return status
    except requests.exceptions.RequestException as exception:
        print(exception)
        sys.exit(1)

def change_name(name):
    try:
        name_req = requests.post(
            f"{url}/api/adv/change_name/",
            headers={
                "Authorization": f"Token {key}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "name": f"{name}",
                "confirm": "aye"
            })
        )
        name_req.raise_for_status()
        name = name_req.json()
        cooldown = name["cooldown"]
        time.sleep(cooldown)
        return name
    except requests.exceptions.RequestException as exception:
        print(exception)
        sys.exit(1)

def examine_item(item):
    try:
        examine_req = requests.post(
            f"{url}/api/adv/examine/",
            headers={
                "Authorization": f"Token {key}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "name": f"{item}"
            })
        )
        examine_req.raise_for_status()
        examine = examine_req.json()
        cooldown = examine["cooldown"]
        time.sleep(cooldown)
        return examine
    except requests.exceptions.RequestException as exception:
        print(exception)
        sys.exit(1)

def get_last_proof():
    try:
        last_proof_req = requests.get(
            f"{url}/api/bc/last_proof/",
            headers={
                "Authorization": f"Token {key}",
                "Content-Type": "application/json"
            }
        )
        last_proof = last_proof_req.json()
        cooldown = last_proof["cooldown"]
        time.sleep(cooldown)
        return last_proof
    except requests.exceptions.RequestException as exception:
        print(exception)
        sys.exit(1)

def mine_coin(proof):
    try:
        proof_req = requests.post(
            f"{url}/api/bc/mine/",
            headers={
                "Authorization": f"Token {key}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "proof": proof
            })
        )
        proof_req.raise_for_status()
        p = proof_req.json()
        cooldown = p["cooldown"]
        time.sleep(cooldown)
        return p
    except requests.exceptions.RequestException as exception:
        print(exception)
        sys.exit(1)

def examine_well():
    try:
        examine_req = requests.post(
            f"{url}/api/adv/examine/",
            headers={
                "Authorization": f"Token {key}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "name": "well"
            })
        )
        examine_req.raise_for_status()
        examine = examine_req.json()
        cooldown = examine["cooldown"]
        time.sleep(cooldown)
        return examine
    except requests.exceptions.RequestException as exception:
        print(exception)
        sys.exit(1)
