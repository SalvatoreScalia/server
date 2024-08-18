import asyncio
import websockets
import json
import copy
import ssl
from aiohttp import web
from aiohttp.web_middlewares import middleware
from controller import guardar_datos, cargar_datos, GameStage, dateTimeLib,Competitor,generate_id

stop_server = False
connected_clients = set()

# Config headers CORS
def configure_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Accept'
    return response

# Middleware  CORS
@middleware
async def cors_middleware(request, handler):
    if request.method == 'OPTIONS':
        response = web.Response(status=200)
        return configure_cors_headers(response)
    else:
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

# Management of login
async def handle_login(request):
    try:
        data = await request.json()
        username_key = data.get('username')
        unencrypted_password = data.get('password')
        user = users.get(username_key)
        if user and user['password'] == unencrypted_password:
            print(f"{user['nick_name']} ha entrado en la partida.")
            user['status'] = f'last-login: {dateTimeLib.now().strftime("%Y-%m-%d %H:%M:%S")}'
            return web.json_response({
                #'status': 'success',
                'role': user['role'],
                'user_id':user['user_id'],
                'nick':user['nick_name'],
                'competitor_id':user['competitor_id']
                })
        else:
            return web.json_response({'status': 'error'}, status=401)
    except json.JSONDecodeError:
        return web.json_response({'status': 'error','message': 'Invalid JSON'},status=400)

# Sent the stage of game to the clients
async def tx_stage_of_game():
    global stop_server
    print("Start websocket connection and send messages.")
    try:
        while not stop_server:
            message = json.dumps([game_stage.to_dict() for game_stage in game_stages])
            for client in connected_clients:
                await client.send(message)
            await asyncio.sleep(0.1)
    except websockets.ConnectionClosed as wscc:
        print(f"The connection is closed with send message: {wscc}")
    finally:
        print('End send states.')

# Handle chat messages
async def handle_chat_message(dict_message):
    chat_message = json.dumps({
        "type": "chat",
        "message": dict_message['content'],
        "sender": dict_message['sender']
    })
    print(f"Chat message from {dict_message['sender']}: {dict_message['content']}")
    for client in connected_clients:
        await client.send(chat_message)

# Handle notifications
async def send_notifications(dict_message):
    notification_message = json.dumps({
        "type": "notification",
        "content": dict_message['content'],
    })
    print(f"Notification: {dict_message['content']}")
    for client in connected_clients:
        await client.send(notification_message)

# Recive the commands
async def rx_commands(websocket, path):
    global stop_server
    if path not in ("/chat", "/notifications", "/game"):
        print("The path must by chat, notifications or game!")
        websockets.ConnectionClosed
    else:
        connected_clients.add(websocket)
    try:
        async for message in websocket:
            try:
                dict_message = json.loads(message)
                if path == "/chat":
                    await handle_chat_message(dict_message)
                elif path == "/notifications":
                    await send_notifications(dict_message)
                elif path == "/game":
                    command = dict_message['command']
                    if command == "/stop":
                        stop(dict_message)
                        break
                    elif command == "/restore":
                        restore(dict_message)
                    elif command == "/save":
                        save(dict_message)
                    elif command == "/new_game":
                        new_game(dict_message)
            except json.JSONDecodeError:
                print("Error when decode JSON.")
            except Exception as e:
                print(f"Error: {e}")
    except websockets.ConnectionClosed as wscc:
        print(f"Connection closed with the client: {wscc}")
    finally:
        connected_clients.remove(websocket)
        print(f"End receive commands.")

#init of root in static and go to index.html
async def handle_root(request):
    # Redirige a /static/index.html
    raise web.HTTPFound('/static/index.html')

# Init server
async def start_server():
    global stop_server
    #cert
    #ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    #ssl_context.load_cert_chain(certfile='certificates/certificate.pem', keyfile='certificate/private_key.pem')

    # Configuración del servidor HTTP (login)
    app = web.Application(middlewares=[cors_middleware])
    app.router.add_post('/login', handle_login)
    app.router.add_get('/', handle_root)# Ruta para manejar la raíz
    app.router.add_static('/static', './static')
    
    # Iniciar el servidor HTTP
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', 8080)#ssl_context=ssl_context
    await site.start()
    
    if current_game:
        pass
        ##websocket_server = await websockets.serve(rx_commands, "127.0.0.1", 3001, ping_interval=60,ping_timeout=10)
    else:
        websocket_server=None

    print("Server WebSocket initialized on wss://127.0.0.1:3001")
    print("Server HTTP for login initialized on http://127.0.0.1:8080")

    try:
        # Tarea para enviar estados continuamente
        enviar_estado_task = asyncio.create_task(tx_stage_of_game())
        while not stop_server:
            await asyncio.sleep(1)
    except asyncio.CancelledError as ce:
        print(f"Detected stop: {ce}")
    finally:
        enviar_estado_task.cancel()
        websocket_server.close()
        await websocket_server.wait_closed()
        await runner.cleanup()
        print("Server closed.")

#function command
def stop(dict_message):
    global stop_server
    if dict_message == "stop":
        print("Recive stop command save and exit.")
        guardar_datos(users, game_stages)  # Guardar datos al detener el servidor
        stop_server = True
def restore(dict_message):
    index = dict_message.get("index")
    competitor_id = dict_message.get("competitor_id")
    if 0 <= index < len(game_stages):# Access the stage directly using the index if the index is valid
        stage = game_stages[index]                        
        stage.is_active = True
        
        guardar_datos(users=users, list_of_game_stages=game_stages)# Save data after updating #function for remove all stages after is_active = True
    else:
        print(f"Error: Index {index} is out of range.")
def save(dict_message):
    competitor_id = dict_message.get("competitor_id")
    current_game.base_entity_id = generate_id()
    current_game.update_last_edit_by_competitor_id(competitor_id)
    game_stages.append(current_game)
    print_all_game_stages(game_stages)
    guardar_datos(users,game_stages)
def update(dict_message):
    pass
def new_game(dict_message):
    global current_game
    competitor = dict_message.get("competitor")
    new_game_config = dict_message.get("new_game_config")
    competitor_class = Competitor(role=competitor['role'],nick_name=competitor['nick_name'])
    new_game = GameStage(competitor_creator=competitor_class,list_of_competitors=new_game_config['list_of_competitors'],world_name=new_game_config['world_name'],state=new_game_config['state'])
    game_stages.append(new_game)
    current_game = copy.deepcopy(new_game)
    guardar_datos(users,game_stages)

def print_all_game_stages(list_of_game_stages):
    for stage in list_of_game_stages:  # imprimir que se está guardando
            stage.print_data_of_game_stage()

if __name__ == "__main__":
    users, game_stages = cargar_datos()
    current_game = copy.deepcopy(game_stages[0] if game_stages[0].is_active else TypeError("The last element of the list is not active (fix: attribute is_active = True).")) #pendiente generar una nueva instancia GameStage
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("Servidor detenido manualmente Ctrl^C.")
