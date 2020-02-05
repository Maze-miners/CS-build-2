from map.structures import Queue, Stack
from map.functions import move_player, init_player, init_move
from treasure.models import MapRoom
from decouple import config
import random
import json
import pdb
import sys

# exec(open("./map/build-map.py").read())

class Graph:
    def __init__(self):
        self.rooms_count = 0
        self.rooms = {}
    
    def add_room(self, room):
        # add vertex to the graph with dictionary as value
        if room["room_id"] not in self.rooms:
            directions = {}
            for direct in room["exits"]:
                directions[direct] = "?"
            self.rooms[room["room_id"]] = directions
            self.rooms_count +=1
            # save vertex to the database
            map_room = MapRoom(room_id=room["room_id"], title=room["title"], description=room["description"], coordinates=str(room["coordinates"]))
            map_room.neighbors = json.dumps(directions)
            map_room.save()
        else:
            print(f"room: {room} already exists, did not add.")
            return False
    
    def connect_rooms(self, next_dir, curr_room, prev_room):
        for direction in self.rooms[prev_room]:
            if direction == next_dir:
                self.rooms[prev_room][direction] = curr_room
        for direction in list(self.rooms[curr_room]):
            if next_dir == "n":
                self.rooms[curr_room]["s"] = prev_room
            if next_dir == "s":
                self.rooms[curr_room]["n"] = prev_room
            if next_dir == "e":
                self.rooms[curr_room]["w"] = prev_room
            if next_dir == "w":
                self.rooms[curr_room]["e"] = prev_room
        # get room from database, update, save
        prev_map_room = MapRoom.objects.get(room_id=prev_room)
        prev_map_room.neighbors = json.dumps(self.rooms[prev_room])
        prev_map_room.save()
        curr_map_room = MapRoom.objects.get(room_id=curr_room)
        curr_map_room.neighbors = json.dumps(self.rooms[curr_room])
        curr_map_room.save()
    
    def dft_rand(self, init_room, pr, rd):
        stack = Stack()
        stack.push(init_room)
        prev_room = pr
        random_dir = rd
        
        while len(self.rooms) <= 500:
            curr_room = stack.pop()
            print("***", curr_room["room_id"])
            if curr_room["room_id"] not in self.rooms:
                # add to graph and save to database
                self.add_room(curr_room)
                print(curr_room["room_id"], "added to self.rooms")
            if random_dir == 'None': # string type from .txt file
                dir_list = []
                for direction in self.rooms[curr_room["room_id"]]:
                    if self.rooms[curr_room["room_id"]][direction] == "?":
                        dir_list.append(direction)
                    random.shuffle(dir_list)
                    random_dir = dir_list.pop()
                    # write to file
                    f = open("random_dir.txt", "w")
                    f.write(random_dir)
                    f.close()
            if prev_room != 'None':
                # connect rooms 
                self.connect_rooms(random_dir, curr_room["room_id"], prev_room["room_id"])
                print(curr_room["room_id"], "connected to:", prev_room["room_id"])
            if random_dir not in self.rooms[curr_room["room_id"]]:
                print("random_dir", random_dir, "self.rooms[curr_room.id]:", self.rooms[curr_room["room_id"]])
                unex_list = []
                for key, value in self.rooms[curr_room["room_id"]].items():
                    # add all directions with unexplored exits
                    if value == "?":
                        unex_list.append(key)
                print("unex_list", unex_list)
                if len(unex_list) == 0:
                    # perform bfs if no unexplored exits
                    path = self.bfs(curr_room)
                    print("path:", path)
                    if path is None:
                        print("path is none")
                        return
                    new_room = path[-1][0]
                    print("path[-1][0]:", path[-1][0])
                    for move in path[1:]:
                        # move in direction provided by bfs
                        print(move)
                        prev_room = curr_room
                        # write to file
                        f = open("prev_room.txt", "w")
                        f.write(f"{prev_room['room_id']}")
                        f.close()
                        curr_room = move_player(move[1], prev_room["room_id"])                   
                    unex_list = []
                    for key, value in self.rooms[new_room].items():
                        if value == "?":
                            unex_list.append(key)
                    
                    random.shuffle(unex_list)
                
                random_dir = unex_list.pop()
                # write to file
                f = open("random_dir.txt", "w")
                f.write(random_dir)
                f.close()
            
            prev_room = curr_room
            # write to file
            f = open("prev_room.txt", "w")
            f.write(f"{prev_room['room_id']}")
            f.close()

            # iterate
            curr_room = move_player(random_dir, prev_room["room_id"])
            stack.push(curr_room)
    
    def bfs(self, first_room):
        queue = Queue()
        queue.enqueue([(first_room["room_id"], "")])
        visited_set = set()
        
        while queue.size() > 0 and len(self.rooms) < 500:
            new_path = queue.dequeue()
            room = new_path[-1][0]
            for direction, value in self.rooms[room].items():
                if value == "?":
                    return new_path
            if room not in visited_set:
                visited_set.add(room)
                for direction, neighbor in self.rooms[room].items():
                    if neighbor not in visited_set:
                        next_path = list(new_path)
                        next_path.append((neighbor, direction))
                        queue.enqueue(next_path)

user = init_player()
tg = Graph()

rooms = MapRoom.objects.all()
for room in rooms:
    # fill in our graph from populated database
    tg.rooms[room.room_id] = json.loads(room.neighbors)

# extract previous room_id
p = open("prev_room.txt", "r")
pre_room = p.read()
prev_room = int(pre_room)
p.close()

# extract previous random dir
r = open("random_dir.txt", "r")
random_dir = r.read()
r.close()

opposite = {"n": "s", "s": "n", "e": "w", "w": "e"}

# if picking back up after interrupt
if prev_room != "None":
    # capture previous room object from API by moving
    roomObj = init_move(opposite[random_dir])
    # return to starting room
    move_player(random_dir, prev_room)
else:
    roomObj = prev_room

# tg.dft_rand(user, roomObj, random_dir)
