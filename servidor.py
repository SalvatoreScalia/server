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

# Receive the commands
async def rx_commands(websocket, path, users_, list_):

    # add new client in the list of path
    ACTIVE_ROUTES[path].add(websocket)
    print(f"New client connected to {path}: {websocket.remote_address}")
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
        print(f"Connection closed with the client: {wscc}")
    finally:
        ACTIVE_ROUTES[path].remove(websocket)
        print(ACTIVE_ROUTES)
        if not ACTIVE_ROUTES[path]:  # Si no quedan clientes en la ruta, eliminar la ruta
            print('ACTIVE_ROUTES is void:')
            #del ACTIVE_ROUTES[path]
        print(f"Client disconnected from {path}: {websocket.remote_address}")
        
# Send game state to clients
async def tx_stage_of_game():
    print("called tx_stage_of_game()")
    try:
        while not STOP_SERVER:
            async with LIST_LOCK:
                for path, clients in ACTIVE_ROUTES.items():
                    if clients:  # Send only if there are clients connected to this path
                        message = json.dumps([game_stage.to_dict() for game_stage in list_game_stages])
                        print(f"Sending [game_stage] to {path}: {message}")
                        for client in clients:
                            try:
                                await client.send(message)
                            except websockets.ConnectionClosed as wscc:
                                print(f"The connection to {client.remote_address} on path {path} is closed: {wscc}")
            await asyncio.sleep(0.1)
    except websockets.ConnectionClosed as wscc:
        print(f"The connection is closed while sending message: {wscc}")
    finally:
        print('Stopped sending game states.')

def stop(users_,list_game_stages_,dict_message):
    global STOP_SERVER
    print("Received stop command, saving and exiting.")
    scapeSave = dict_message.get('scapeSave') or False
    if not scapeSave:
        write_json_data(users_, list_game_stages_)
    STOP_SERVER = True
    
def save(users_, list_game_stages_,dict_message):
    try:
        gameStage = dict_message.get('gameStage')
        overwriteLastGameStage = dict_message.get('overwriteLastGameStage') or False
        newgame = GameStage(**gameStage)
        if not overwriteLastGameStage:
            newgame.new_id()
            list_game_stages_.insert(newgame)
        else:
            list_game_stages_[0] = newgame
        write_json_data(game_id,users_, list_game_stages_)
    except Exception as ex:
        print(f'Error when save{ex}')
    

def restore(users_,list_,dict_message):
    index = dict_message.get("index")
    if 0 <= index < len(list_):
        list_[index].is_active = True
    else:
        print(f"Error: Index {index} is out of range.")

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
    print(f"the status of list of game n. {index} now is {list_[index].state}")

# Start the WebSocket server
async def start_websocket(host, port, path_from_http, game_id_from_http, ping_interval, ping_timeout):
    global users,list_game_stages,game_id
    game_id = game_id_from_http if game_id_from_http is not None else generate_id()
    users,list_game_stages = read_json_data(game_id)

    websocket_server = await websockets.serve(
        lambda ws, path=path_from_http: rx_commands(ws, path, users, list_game_stages),
        host=host,
        port=port,
        ping_interval=ping_interval,
        ping_timeout=ping_timeout
    )
    print(f"Server WebSocket initialized on ws://{host}:{port} with game_id {game_id_from_http}")

    enviar_estado_task = asyncio.create_task(tx_stage_of_game(list_game_stages))
    try:
        while not STOP_SERVER:
            await asyncio.sleep(1)
    except asyncio.CancelledError as ce:
        print(f"Detected stop: {ce}")
    finally:
        print("WebSocket server closed.")
        enviar_estado_task.cancel()
        websocket_server.close()
        await websocket_server.wait_closed()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start a WebSocket server")
    parser.add_argument("--host", default="127.0.0.1", help="Host address")
    parser.add_argument("--port", type=int, default=3001, help="Port number")
    parser.add_argument("--path", default="/", help="Server path")
    parser.add_argument("--game_id", required=False, help="ID of file (id.json) of the game hosted by this server")
    parser.add_argument("--ping_interval", type=int, default=60, help="Ping interval in seconds (default: 60)")
    parser.add_argument("--ping_timeout", type=int, default=60, help="Ping timeout in seconds (default: 60)")

    args = parser.parse_args()

    asyncio.run(start_websocket(args.host, args.port, args.path, args.game_id, args.ping_interval, args.ping_timeout))