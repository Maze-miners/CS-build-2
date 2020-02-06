from map.functions import check_status, init_player, check_status
from map.build import Graph
from treasure.models import MapRoom
import json
# import re
# import sys
import os
# import time
import random
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
    user = init_player()
    # status = check_status()
    # print(bcolors.HEADER + bcolors.BOLD + f"\nWelcome {status["name"]}" + bcolors.ENDC + bcolors.ENDC)
    # print(bcolors.ITALIC + f"{user["title"]} (Room {user["room_id"]})" + bcolors.ENDC)
    # print(bcolors.ITALIC + f"{user["description"]}" + bcolors.ENDC)

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
        # bring app to top of terminal screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        if prompt == 'o':
            print(
                "\nOPTIONS:"
                "\n[r] Travel to random room, collecting treasure until inventory is full"
                "\n[ts] Travel to the shop"
                "\n[tr] Travel to see Pirate Ry"
                "\n[sa] Sell all items (must be at Shop)"
                "\n[n] Purchase a name (must be Pirate Ry's)"
                "\n[w] Travel to the wishing well"
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
            pass

        elif prompt == 'tr':
            pass

        elif prompt == 'sa':
            pass

        elif prompt == 'n':
            pass

        elif prompt == 'w':
            pass

        elif prompt == 'm':
            pass
        
        else:
            print(bcolors.FAIL + "\nInvalid choice" + bcolors.ENDC)

        print(
            "\nWhat would you like to do?"
            "\n[o] See all options"
            "\n[c] Check status"
            "\n[q] Save and Quit"
        )
        prompt = input(bcolors.HEADER + "\n>>> " + bcolors.ENDC).lower()

    # bring app to top of terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')
    print(bcolors.ITALIC + "\nGoodbye\n" + bcolors.ENDC)


app()
