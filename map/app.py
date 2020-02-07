from map.functions import check_status, init_player, check_status, sell_all_items, change_name, examine_well, translate_code
from map.build import Graph
from map.miner import mine_for_coin
from treasure.models import MapRoom
import json
import os
import random
import time

# exec(open("./map/app.py").read())

class bcolors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    ITALIC = '\033[3m'
    ENDC = '\033[0m'

def app():
    # populate graph from database
    graph = Graph()
    rooms = MapRoom.objects.all()
    for room in rooms:
        # fill in our graph from populated database
        graph.rooms[room.room_id] = json.loads(room.neighbors)

    # bring app to top of terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')

    # init player and welcome by name
    print("\n...")
    user = init_player()
    status = check_status()
    print(bcolors.HEADER + bcolors.BOLD + "\nWelcome " + status["name"] + bcolors.ENDC + bcolors.ENDC)
    print(bcolors.ITALIC + "You are in room " + str(user["room_id"]) + " - " + user["title"] + bcolors.ENDC)
    print(bcolors.ITALIC + user["description"] + bcolors.ENDC)

    print(bcolors.HEADER + bcolors.BOLD + "\nWelcome [USER]" + bcolors.ENDC + bcolors.ENDC)

    # print current room and prompt player to make a move

    # should check to make sure graph is filled in
    # if not, prompt user to explore all rooms before giving prompt to go to specific rooms

    # will need to add kwargs for examine, single sale, check status
    print(
        "\nWhat would you like to do?"        
        "\n[o] See all options"
        "\n[c] Check status"
        "\n[q] Save and Quit"
    )

    prompt = input(bcolors.HEADER + "\n>>> " + bcolors.ENDC).lower()
    
    while not prompt == 'q': # game loop

        os.system('cls' if os.name == 'nt' else 'clear')

        print("\n...")
        user = init_player()
        os.system('cls' if os.name == 'nt' else 'clear')
        
        if prompt == 'o':
            print(
                "\nOPTIONS:"
                "\n[r] Travel randomly and pick up treasure"
                "\n[ts] Travel to the shop"
                "\n[tr] Travel to see Pirate Ry"
                "\n[ti] Travel to spcified room number"
                "\n[sa] Sell all items (must be at Shop)"
                "\n[n] Purchase a name (must be Pirate Ry's)"
                "\n[tw] Travel to the wishing well"
                "\n[ew] Examine the wishing well"
                "\n[m] Mine"
            )

        elif prompt == 'c':
            print('\n...')
            status = check_status()
            print(bcolors.BOLD + "\nSTATUS" + bcolors.ENDC)
            for key in status:
                print(f"{key}: {status[key]}")
        
        elif prompt == 'r':
            print("\n...")
            rand_room = random.randint(0, 500)
            graph.dft_treasure(user, rand_room)

        elif prompt == 'ts':
            graph.dft_treasure(user, 1)

        elif prompt == 'tr':
            graph.dft_treasure(user, 467)

        elif prompt == 'ti':
            print(bcolors.ITALIC + "\nWhich room number would you like to travel to?" + bcolors.ENDC)
            room_prompt = input(bcolors.HEADER + "\n>>> " + bcolors.ENDC)
            try:
                room_int = int(room_prompt)
                if 0 <= room_int <= 499:
                    graph.dft_treasure(user, room_int)
                else:
                    print(bcolors.FAIL + "\nInvalid room number" + bcolors.ENDC)
            except:
                print(bcolors.FAIL + "\nInvalid room number" + bcolors.ENDC)
            
        elif prompt == 'sa':
            sell_all_items()

        elif prompt == 'n':
            print(bcolors.ITALIC + "\nWhat would you like to change your name to?" + bcolors.ENDC)
            name_prompt = input(bcolors.HEADER + "\n>>> " + bcolors.ENDC).lower()
            try:
                if len(name_prompt) > 0:
                    change_name(name_prompt)
                else:
                    print(bcolors.FAIL + "\nInvalid name" + bcolors.ENDC) 
            except:
                print(bcolors.FAIL + "\nInvalid name" + bcolors.ENDC)

        elif prompt == 'tw':
            graph.dft_treasure(user, 55)

        elif prompt == 'm':
            mine_for_coin()

        elif prompt == 'ew':
            print("\n...")
            print("\nPeering into the well...")
            time.sleep(1.5)
            print("Translating code...")
            well = examine_well()
            message = well["description"]
            code = message[41:]
            f = open("map/ls8/examine_well.ls8", "w")
            f.write(code)
            f.close()
            c = translate_code()
            print(c)
        
        else:
            print(bcolors.FAIL + "\nInvalid choice" + bcolors.ENDC)

        print(
            "\nWhat would you like to do?"
            "\n[o] See all options"
            "\n[c] Check status"
            "\n[q] Save and Quit"
        )
        prompt = input(bcolors.HEADER + "\n>>> " + bcolors.ENDC).lower()

    os.system('cls' if os.name == 'nt' else 'clear')
    print(bcolors.ITALIC + "\nGoodbye\n" + bcolors.ENDC)


app()
