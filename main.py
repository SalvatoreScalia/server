import asyncio
import json
from aiohttp import web
from aiohttp.web_middlewares import middleware
from servidor import start_websocket
from controller import read_json_data, dateTimeLib

SERVER_ON = True
websocket_task = None
websocket_is_active = False
users, list_gs = read_json_data()

# Config headers CORS
def configure_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Accept'
    return response

# Middleware CORS
@middleware
async def cors_middleware(request, handler):
    if request.method == 'OPTIONS':
        print("Handling OPTIONS request for CORS")
        response = web.Response(status=200)
        return configure_cors_headers(response)
    else:
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return configure_cors_headers(response)

async def handle_home(request):
    return web.FileResponse('./static/index.html')

async def handle_login_page(request):
    return web.FileResponse('./static/login.html')

async def handle_player(request):
    return web.FileResponse('./static/player.html')

async def handle_master(request):
    return web.FileResponse('./static/master.html')

# Management of login
async def handle_login(request):
    try:
        data = await request.json()
        username_key = data.get('username')
        unencrypted_password = data.get('password')
        user = users.get(username_key)
        if user and user['password'] == unencrypted_password:
            print(f"{user['user_nickname']} has entered the game.")
            user[
                'status'] = f'last-login: {dateTimeLib.now().strftime("%Y-%m-%d %H:%M:%S")}'
            return web.json_response({
                'role': user['role'],
                'user_id': user['user_id'],
                'user_nickname': user['user_nickname'],
                'competitor_id': user['competitor_id']
            })
        else:
            return web.json_response({'status': 'error'}, status=401)
    except json.JSONDecodeError:
        return web.json_response({'status': 'error', 'message': 'Invalid JSON'}, status=400)

# Endpoint to start the WebSocket server
async def handle_start_websocket(request):
    global websocket_is_active,websocket_task
    data = await request.json()
    print(data)
    if not websocket_is_active:
        websocket_task = asyncio.create_task(start_websocket(users=users, list_game_stages=list_gs))
        websocket_is_active = True
        return web.json_response({
            'status': 'success',
            'message': 'WebSocket server started.'
        })
    else:
        return web.json_response({
            'status': 'warning',
            'message': 'WebSocket server is already running.'
        })

async def monitor_websocket_task():
    global websocket_is_active
    while not websocket_task.done():
        await asyncio.sleep(1)
    print("WebSocket server has fully terminated.")
    websocket_is_active = False

# Init server
async def start_server():

    routes = [
        web.get('/', handle_home),  # Redirige la raíz a /home
        web.get('/home', handle_home),  # Muestra el contenido de index.html
        web.get('/login', handle_login_page),  # Muestra el contenido de login.html
        web.get('/player', handle_player),  # Muestra el contenido de index.html
        web.get('/master', handle_master),  # Muestra el contenido de login.html
        web.post('/login', handle_login),
        web.post('/start_websocket', handle_start_websocket),
        web.static('/static', './static')
    ]

    # Creación de la aplicación con middleware y rutas
    app = web.Application(middlewares=[cors_middleware])
    app.add_routes(routes)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', 8080)

    print("Server HTTP for login initialized on http://127.0.0.1:8080")
    try:
        await site.start()
        if websocket_task:
            asyncio.create_task(monitor_websocket_task())
        while SERVER_ON:
            await asyncio.sleep(1)
    except asyncio.CancelledError as ce:
        print(f"Detected stop: {ce}")
    finally:
        await runner.cleanup()
        print("Server closed.")

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("Servidor detenido manualmente con Ctrl+C.")
