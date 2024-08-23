import asyncio
import websockets
import json
from controller import write_json_data
from classes import GameStage,Competitor

CONNECTED_CLIENTS = set()
STOP_SERVER = False
LIST_LOCK = asyncio.Lock()  # Lock para proteger list_game_stages

# Recibe los comandos
async def rx_commands(websocket, path, users_, list_):
    global STOP_SERVER
    if path == "/chat":
        await handle_chat_message(dict_message)
    elif path == "/notifications":
        await send_notifications(dict_message)
    elif path != "/game":
        print("Path must be /game to be added to CONNECTED_CLIENTS!")
        return
    
    CONNECTED_CLIENTS.add(websocket)  # Añadir cliente a CONNECTED_CLIENTS
    print(f"New client connected: {websocket.remote_address}")
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
        CONNECTED_CLIENTS.remove(websocket)  # Remover cliente de CONNECTED_CLIENTS
        print(f"Client disconnected: {websocket.remote_address}")
        
# Envía el estado del juego a los clientes
async def tx_stage_of_game(list_game_stages):
    global STOP_SERVER
    print("Start sending game stages to clients.")
    try:
        while not STOP_SERVER:
            async with LIST_LOCK:
                if CONNECTED_CLIENTS:  # Enviar solo si hay clientes conectados
                    message = json.dumps([game_stage.to_dict() for game_stage in list_game_stages])
                    for client in CONNECTED_CLIENTS:
                        await client.send(message)
                await asyncio.sleep(0.1)
    except websockets.ConnectionClosed as wscc:
        print(f"The connection is closed while sending message: {wscc}")
    finally:
        print('Stopped sending game states.')


# Handle chat messages
async def handle_chat_message(dict_message):
    chat_message = json.dumps({
        "type": "chat",
        "message": dict_message['content'],
        "sender": dict_message['sender']
    })
    print(f"Chat message from {dict_message['sender']}: {dict_message['content']}")
    for client in CONNECTED_CLIENTS:
        await client.send(chat_message)

# Handle notifications
async def send_notifications(dict_message):
    notification_message = json.dumps({
        "type": "notification",
        "content": dict_message['content'],
    })
    print(f"Notification: {dict_message['content']}")
    for client in CONNECTED_CLIENTS:
        await client.send(notification_message)


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
        write_json_data(users_, list_game_stages_)
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

# Inicia el servidor WebSocket
async def start_websocket(users, list_game_stages):
    global STOP_SERVER

    websocket_server = await websockets.serve(lambda ws, path: rx_commands(ws, path, users, list_game_stages),
                                              "127.0.0.1", 3001, ping_interval=60, ping_timeout=60)
    print("Server WebSocket initialized on ws://127.0.0.1:3001")
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

# Aquí puedes agregar otras funciones auxiliares según sea necesario