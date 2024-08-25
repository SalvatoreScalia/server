import asyncio
import websockets
import json
import argparse
from classes import GameStage,Competitor,generate_id
from controller import write_json_data,read_json_data
from shared_data import ACTIVE_ROUTES

STOP_SERVER = False
LIST_LOCK = asyncio.Lock()  # Lock para proteger list_game_stages
users = None
list_game_stages = None
file_name = None

# Receive the commands
async def rx_commands(websocket, path, users_, list_):

    # add new client in the list of path
    ACTIVE_ROUTES[path].add(websocket)
    print(f"[async rx_]New client connected to {path}: {websocket.remote_address}")
    try:            
        async for message in websocket:
            dict_message = json.loads(message)
            command = dict_message['command']
            async with LIST_LOCK:
                if command == "/stop":
                    stop(users_, list_, dict_message)
                    break
                elif command == "/restore":
                    restore(users_, list_, dict_message)
                elif command == "/save":
                    save(users_, list_, dict_message)
                elif command == "/newGame":
                    new_game(users_, list_, dict_message)
                elif command == "/autobinding":
                    auto_binding(users_, list_, dict_message)
                elif command == "/updateState":
                    update_state_to_text_(users_, list_, dict_message)
    except websockets.ConnectionClosed as wscc:
        print(f"[async rx_]Connection closed:  {wscc}")
    finally:
        ACTIVE_ROUTES[path].remove(websocket)
        if not ACTIVE_ROUTES[path]:
            print('ACTIVE_ROUTES is void:')
            #del ACTIVE_ROUTES[path]
        print(f"[async rx_]Client disconnected from {path}: {websocket.remote_address}")
        
# Send game state to clients
async def tx_stage_of_game():
    try:
        while not STOP_SERVER:
            async with LIST_LOCK:
                for path, clients in ACTIVE_ROUTES.items():
                    if clients:  # Send only if there are clients connected to this path
                        message = json.dumps([game_stage.to_dict() for game_stage in list_game_stages])
                        for client in clients:
                            try:
                                await client.send(message)
                            except websockets.ConnectionClosed as wscc:
                                print(f"[async tx_]The connection to {client.remote_address} on path {path} is closed: {wscc}")
            await asyncio.sleep(0.1)
    except websockets.ConnectionClosed as wscc:
        print(f"[async tx_]The connection is closed while sending message: {wscc}")
    finally:
        print('Stopped sending game states.')

def stop(users_,list_game_stages_,dict_message):
    global STOP_SERVER
    print("[stop]Received stop command from game, saving and exiting.")
    scapeSave = dict_message.get('scapeSave') or False
    if not scapeSave:
        write_json_data(file_name or 'data',users_, list_game_stages_)
    STOP_SERVER = True
    
def save(users_, list_game_stages_,dict_message):
    try:
        gameStage = dict_message.get('gameStage')
        overwriteLastGameStage = dict_message.get('overwriteLastGameStage') or False
        fileName=dict_message.get('fileName') or file_name or 'data'
        newgame = GameStage(**gameStage)
        if not overwriteLastGameStage:
            newgame.new_id()
            list_game_stages_.insert(newgame)
        else:
            list_game_stages_[0] = newgame
        write_json_data(fileName,users_, list_game_stages_)
    except Exception as ex:
        print(f'[save]Error when save:{ex}')
    

def restore(users_,list_,dict_message):
    index = dict_message.get("index")
    if 0 <= index < len(list_):
        list_[index].is_active = True
    else:
        print(f"[restore]Error: Index {index} is out of range.")

def new_game(users_,list_,dict_message):
    competitor = dict_message.get("competitor")
    newGameConfig = dict_message.get("newGameConfig")
    newGame = GameStage(creator_competitor_id=competitor['base_entity_id'],#possible error en futuro soulcion id
                         list_of_competitors=newGameConfig.get('listOfCompetitors'),
                         world_name=newGameConfig.get('worldName'), 
                         state=newGameConfig.get('state'))
    list_.insert(newGame)

def auto_binding(users_,list_,dict_message):
    gameStage = dict_message.get('gameStage')
    index = dict_message.get('index') or 0
    list_[index].update_attributes_recursive(gameStage)

def update_state_to_text_(users_,list_,dict_message):
    text = dict_message.get('text')
    index = dict_message.get('index') or 0
    list_[index].update_state_(text)
    print(f"[update_state_to_text]The status in list of game n. {index} now is {list_[index].state}")

# Start the WebSocket server
async def start_websocket(host_, port_, path_, ping_interval_, ping_timeout_, file_name_ = None):
    global users,list_game_stages,file_name
    file_name=file_name_
    users,list_game_stages = read_json_data(file_name=file_name_)

    try:
        websocket_server = await websockets.serve(
            lambda ws, path=path_: rx_commands(ws, path, users, list_game_stages),
            host=host_,
            port=port_,
            ping_interval=ping_interval_,
            ping_timeout=ping_timeout_
        )
        print(f"[async start_websocket]Server WebSocket initialized on wss://{host_}:{port_}{path_} with file name: {file_name_}")

        tx_task = asyncio.create_task(tx_stage_of_game())
        while not STOP_SERVER:
            await asyncio.sleep(1)
    except asyncio.CancelledError as ce:
        print(f"[async start_websocket] Detected error: {ce}")
    finally:
        print("[async start_websocket] Closing server...")
        tx_task.cancel()
        websocket_server.close()
        await websocket_server.wait_closed()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start a WebSocket server")
    parser.add_argument("--host", default="127.0.0.1", help="Host address")
    parser.add_argument("--port", type=int, default=3001, help="Port number")
    parser.add_argument("--path", default="/game", help="Server path")
    parser.add_argument("--ping_interval", type=int, default=60, help="Ping interval in seconds (default: 60)")
    parser.add_argument("--ping_timeout", type=int, default=60, help="Ping timeout in seconds (default: 60)")
    parser.add_argument("--file_name", required=False, help="name of file (name.json) of the game hosted by this server")

    args = parser.parse_args()

    try:
        asyncio.run(start_websocket(args.host, args.port, args.path, args.ping_interval, args.ping_timeout, args.file_name))
    except KeyboardInterrupt:
        print("[main]Server stopped manually with Ctrl+C.")
    except Exception as e:
        print(f"[main]An unexpected error occurred: {e}")
    finally:
        #
        pass