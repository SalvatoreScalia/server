import asyncio
import json
import re
import subprocess
from datetime import datetime
from aiohttp import web
from aiohttp.web_middlewares import middleware
from shared_data import ACTIVE_ROUTES, DEAFAULT_USERS

SERVER_ON = True
websocket_task = None
websocket_is_active = False

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
        start_port = 8000
        end_port = 8100
        available_ports = find_available_ports(start_port, end_port)
        data = await request.json()
        username_key = data.get('username')
        unencrypted_password = data.get('password')
        user = DEAFAULT_USERS.get(username_key)
        if user and user['password'] == unencrypted_password:
            print(f"{user['user_nickname']} has entered the game.")
            user['status'] = f'last-login: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            return web.json_response({
                'role': user['role'],
                'user_id': user['user_id'],
                'user_nickname': user['user_nickname'],
                'competitor_id': user['competitor_id'],
                'available_ports': available_ports if user['role'] == 'master' else 0
            })
        else:
            return web.json_response({'status': 'error'}, status=401)
    except json.JSONDecodeError:
        return web.json_response({'status': 'error', 'message': 'Invalid JSON'}, status=400)

async def monitor_websocket_task():
    global websocket_is_active
    while not websocket_task.done():
        await asyncio.sleep(1)
    print("WebSocket server has fully terminated.")
    websocket_is_active = False

def get_used_ports():
    result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
    used_ports = set()
    for line in result.stdout.splitlines():
        if 'TCP' in line or 'UDP' in line:
            match = re.search(r':(\d+)\s+', line)
            if match:
                port = int(match.group(1))
                used_ports.add(port)
    return used_ports

def find_available_ports(start_port, end_port):
    used_ports = get_used_ports()
    available_ports = [port for port in range(start_port, end_port + 1) if port not in used_ports]
    return available_ports


# Endpoint to start the WebSocket server
async def handle_start_websocket(request):
    global websocket_is_active,websocket_task
    data = await request.json()
    print('debug logs:')
    print(ACTIVE_ROUTES)
    print(data)
    game_id = data.get('game_id')
    host = data.get('host')
    port = data.get('port')
    path = data.get('path')
    cmd = [
        'python', 'servidor.py',
        '--host', host,
        '--port', port,
        '--path', path,
        '--game_id',game_id
    ]    
    if not websocket_is_active:
        #websocket_task = asyncio.create_task(start_websocket(users=users, list_game_stages=list_gs))
        websocket_task = subprocess.Popen(cmd)
        websocket_is_active = True
        return web.json_response({
            'status': 'success',
            'message': f"WebSocket server started on {host}:{port}/{path}"
        })
    else:
        return web.json_response({
            'status': 'warning',
            'message': 'WebSocket server is already running.'
        })


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
