import asyncio
import json
import re
import subprocess
from datetime import datetime
from aiohttp import web
from aiohttp.web_middlewares import middleware
from shared_data import  DEAFAULT_USERS, ACTIVE_ROUTES

SERVER_ON = True
websocket_tasks = {}
start_port = 3000
end_port = 3050

###################-- Config headers CORS --######################
def configure_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Accept'
    return response

@middleware # Middleware CORS
async def cors_middleware(request, handler):
    if request.method == 'OPTIONS':
        print("Handling OPTIONS request for CORS")
        response = web.Response(status=200)
        return configure_cors_headers(response)
    else:
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return configure_cors_headers(response)
    
########################-- REDIRECT --############################
async def handle_home(request):
    return web.FileResponse('./static/index.html')
async def handle_login_page(request):
    return web.FileResponse('./static/login.html')
async def handle_player(request):
    return web.FileResponse('./static/player.html')
async def handle_master(request):
    return web.FileResponse('./static/master.html')

###################-- MANAGEMENT OF LOGIN --######################
async def handle_login(request):
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.json_response({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    username_key = data.get('username')
    unencrypted_password = data.get('password')
    user = DEAFAULT_USERS.get(username_key)
    if not user or user['password'] != unencrypted_password:
        return web.json_response({'status': 'error','message':'The username or password is incorrect'}, status=401)
    # Logging the user in
    print(f"{user['user_nickname']} has entered the game.")
    user['status'] = f'last-login: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    # Prepare the response based on the user's role
    response_data = {
        'role': user['role'],
        'user_id': user['user_id'],
        'user_nickname': user['user_nickname'],
        'competitor_id': user['competitor_id'],
    }

    return web.json_response(response_data)

##########################-- GET INFO --##########################
async def handle_get_info(request):
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.json_response({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    
    get_ = data.get('data_mapping')#what kind of data
    
    data_mapping = {
        'routes': lambda: {route: len(clients) for route, clients in ACTIVE_ROUTES.items()},
        'ACTIVE_ROUTES': lambda: ACTIVE_ROUTES,
        'websocket_tasks': lambda: websocket_tasks,
        'available_ports': lambda: find_available_ports(start_port, end_port),
    }
    
    if get_ in data_mapping: # Check if the requested key is in the data mapping
        data = data_mapping[get_]()# Call the function mapped to the key
        return web.json_response(data)
    else:
        # Return an error response if the key is not found
        return web.json_response({'status': 'error'}, status=401)

##########################-- SYSTEM --############################
def get_used_ports():
    result = subprocess.run(['ss', '-an'], capture_output=True, text=True)
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

def is_websocket_conflict(host, port, path):
    # Check for conflicts in running WebSocket servers
    for task in websocket_tasks.values():
        if'127.0.0.2' != host:
            return True
        if task['port'] == port or task['path'] == path:#task['host']
                return True
    return False

########################-- start webSocket --#####################
async def monitor_websocket_task(game_id):
    # Monitor the WebSocket task for a specific game
    task = websocket_tasks[game_id]
    while not task['process'].poll():
        await asyncio.sleep(1)
    print(f"WebSocket server for game {game_id} has fully terminated.")
    del websocket_tasks[game_id]

# Endpoint to start the WebSocket server
async def handle_start_websocket(request):
    data = await request.json()
    print('debug logs:')
    print(ACTIVE_ROUTES)
    print(data)
    game_name = data.get('game_name')
    user_nickname = data.get('user_nickname')
    game_id = data.get('game_id')
    host = data.get('host')
    port = int(data.get('port'))
    path = data.get('path')

    # Check if a WebSocket server is already running on the same port or path
    if is_websocket_conflict(host, port, path):
        return web.json_response({
            'status': 'error',
            'message': 'A WebSocket server is already running on this port or path.'
        }, status=400)

    # Create and start the WebSocket server process
    cmd = [
        'python', 'servidor.py',
        '--host', host,
        '--port', str(port),
        '--path', path,
        '--game_id', game_id
    ]
    process = subprocess.Popen(cmd)

    # Store the process and its information in the websocket_tasks dictionary
    websocket_tasks[game_id] = {
        'process': process,
        'host': host,
        'port': port,
        'path': path,
        'user_nickname':user_nickname,
        'players': 0,
        'startTime': str(datetime.now()),
        'game_name':game_name
    }

    # Start monitoring the WebSocket server task
    asyncio.create_task(monitor_websocket_task(game_id))

    return web.json_response({
        'status': 'success',
        'message': f"WebSocket server started on {host}:{port}/{path}"
    })

#---------------------------------------------------| Init server |
async def start_server():
    routes = [
        web.get('/', handle_home),  # Redirect root to /home
        web.get('/home', handle_home),  # Display index.html content
        web.get('/login', handle_login_page),  # Display login.html content
        web.get('/player', handle_player),  # Display player.html content
        web.get('/master', handle_master),  # Display master.html content
        web.post('/get_info',handle_get_info),
        web.post('/login', handle_login),
        web.post('/start_websocket', handle_start_websocket),
        web.static('/static', './static')
    ]

    # Create the application with middleware and routes
    app = web.Application(middlewares=[cors_middleware])
    app.add_routes(routes)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', 8080)

    print("Server HTTP for login initialized on http://127.0.0.1:8080")
    try:
        await site.start()
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