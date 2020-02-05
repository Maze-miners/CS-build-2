import random
from map.structures import Queue, Stack
# import sys
# sys.path.append("/cs-build-2/treasure")
from treasure.models import MapRoom
from map.functions import move_player, init_player
import json
from decouple import config
import pdb
import sys
# exec(open("./map/build-map.py").read())
# curl -X POST -H 'Authorization: Token f44f1bbfeb616d23476784a70a2a4a7543ef202c' -H "Content-Type: application/json" -d '{"direction":"w"}' https://lambda-treasure-hunt.herokuapp.com/api/adv/move/

# view_stack = []
# view_queue = []
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
            map_room = MapRoom(room_id=room["room_id"], title=room["title"], description=room["description"], coordinates=str(room["coordinates"]))
            print("directions: ", directions)
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
        pdb.set_trace()
        prev_map_room = MapRoom.objects.get(room_id=prev_room)
        prev_map_room.neighbors = json.dumps(self.rooms[prev_room])
        prev_map_room.save()
        curr_map_room = MapRoom.objects.get(room_id=curr_room)
        curr_map_room.neighbors = json.dumps(self.rooms[curr_room])
        curr_map_room.save()
    
    def dft_rand(self, init_room, pr, rd):
        stack = Stack()
        stack.push(init_room)
        # view_stack.append(player.current_room.id)
        # # print("initial view stack", view_stack)
        prev_room = pr
        random_dir = rd
        while len(self.rooms) <= 500:
            curr_room = stack.pop()
            # view_stack.pop()
            # # print("view stack after pop", view_stack)
            print("***", curr_room["room_id"])
            if curr_room["room_id"] not in self.rooms:
                self.add_room(curr_room)
                print(curr_room["room_id"], "added to self.rooms")
            if random_dir == 'None':
                dir_list = []
                for direction in self.rooms[curr_room["room_id"]]:
                    print("***", direction)
                    if self.rooms[curr_room["room_id"]][direction] == "?":
                        dir_list.append(direction)
                    random.shuffle(dir_list)
                    random_dir = dir_list.pop()
                    # write
                    f = open("random_dir.txt", "w")
                    f.write(random_dir)
                    f.close()
            print("----", prev_room)
            if prev_room != 'None':
                print("!@#", curr_room["room_id"])
                print("!@#", prev_room)
                self.connect_rooms(random_dir, curr_room["room_id"], prev_room["room_id"])
                print(curr_room["room_id"], "connected to:", prev_room["room_id"])
            if random_dir not in self.rooms[curr_room["room_id"]]:
                print("random_dir", random_dir, "self.rooms[curr_room.id]:", self.rooms[curr_room["room_id"]])
                unex_list = []

                for key, value in self.rooms[curr_room["room_id"]].items():
                    if value == "?":
                        unex_list.append(key)
                print("unex_list", unex_list)
                if len(unex_list) == 0:
                    path = self.bfs(curr_room)
                    print("path:", path)
                    if path is None:
                        print("path is none")
                        return
                    new_room = path[-1][0]
                    print("path[-1][0]:", path[-1][0])
                    for move in path[1:]:
                        print(move)
                        pdb.set_trace()
                        # changing room as we travel
                        prev_room = curr_room
                        curr_room = move_player(move[1])                   
                        # print("player.current_room bfs", player.current_room["room_id"])
                    unex_list = []
                    for key, value in self.rooms[new_room].items():
                        if value == "?":
                            unex_list.append(key)
                    random.shuffle(unex_list)
                random_dir = unex_list.pop()
                # write
                f = open("random_dir.txt", "w")
                f.write(random_dir)
                f.close()
            prev_room = curr_room
            # write
            f = open("prev_room.txt", "w")
            f.write(f"{prev_room['room_id']}")
            f.close()

            curr_room = move_player(random_dir)
            # print("player.current_room dft:", player.current_room.id)
            stack.push(curr_room)
            # view_stack.append(player.current_room.id)
            # # print("from outer cond of dft viewstack", view_stack) 
    
    def bfs(self, first_room):
        queue = Queue()
        queue.enqueue([(first_room["room_id"], "")])
        # view_queue.append([(first_room.id, "")])
        # print("initial view_queue", view_queue)
        visited_set = set()
        while queue.size() > 0 and len(self.rooms) < 500:
            new_path = queue.dequeue()
            # view_queue.pop(0)
            # print("view_queue after dequeue", view_queue)
            room = new_path[-1][0]
            # print("room", room, "new_path", new_path, "queue", queue)
            for direction, value in self.rooms[room].items():
                if value == "?":
                    # print("all of room props:", self.rooms[room])
                    return new_path
            if room not in visited_set:
                visited_set.add(room)
                for direction, neighbor in self.rooms[room].items():
                    if neighbor not in visited_set:
                        next_path = list(new_path)
                        next_path.append((neighbor, direction))
                        queue.enqueue(next_path)
                        # view_queue.append(next_path)
                        # print("viewqueue after append", view_queue)
                        # print("visited_set", visited_set)

user = init_player()
tg = Graph()
rooms = MapRoom.objects.all()
for room in rooms:
    print("&&&", room.neighbors)
    tg.rooms[room.room_id] = json.loads(room.neighbors)

p = open("prev_room.txt", "r")
prev_room = p.read()
p.close()
print(prev_room)
print(bool(prev_room == 'None'))

if prev_room != 'None':
    roomObj = MapRoom.objects.get(room_id=int(prev_room))
    print("!!!", r)
else:
    roomObj = 'None'

r = open("random_dir.txt", "r")
random_dir = r.read()
r.close()
print(random_dir)
tg.dft_rand(user, roomObj, random_dir)