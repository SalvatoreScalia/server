import asyncio
import copy
import ipaddress
import json
import re
import subprocess
from datetime import datetime
import uuid
from aiohttp import web
from aiohttp.web_middlewares import middleware
from shared_data import  DEAFAULT_USERS, ACTIVE_ROUTES

#server seetup:
SERVER_ON = True
HOST = '127.0.0.1'
PORT= 8080
#available_ports:
START_PORT = 3000
END_PORT = 3050
#available_ips:
START_IP = '0.0.0.0'
END_IP = '127.0.0.102'
#webwocket servers in dict:
websocket_server_tasks = {}

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
    print(f"{user['user_nickname']} is now online")
    user['status'] = f'last-login: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    # Prepare the response based on the user's role
    response_data = {
        'role': user['role'],
        'user_id': user['user_id'],
        'user_nickname': user['user_nickname']
    }

    return web.json_response(response_data)

##########################-- GET INFO --##########################
async def handle_get_info(request):
    get_ = request.match_info.get('key')
    
    try:
        data_mapping = {
            'routes': lambda: {route: len(clients) for route, clients in ACTIVE_ROUTES.items()},
            'ACTIVE_ROUTES': lambda: ACTIVE_ROUTES,
            'websocket_server_tasks': lambda: remove_popen_from_dict(websocket_server_tasks),
            'available_ports': lambda: find_available_ports(START_PORT, END_PORT),
        }
        
        if get_ in data_mapping: # Check if the requested key is in the data mapping
            data = data_mapping[get_]()# Call the function mapped to the key
            return web.json_response(data if data else {}, status=204 if not data else 200)
        else:
            # Return an error response if the key is not found
            return web.json_response({'status': 'error'}, status=400)
    except Exception as e:
        print(e)
        return web.json_response({'status': 'error', 'message': str(e)}, status=500)

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
def is_ip_in_range(ip_str, start_ip_str, end_ip_str):
    # Convert IP addresses to IPv4Address objects
    ip = ipaddress.IPv4Address(ip_str)
    start_ip = ipaddress.IPv4Address(start_ip_str)
    end_ip = ipaddress.IPv4Address(end_ip_str)
    # Check if the IP is within the range
    return start_ip <= ip <= end_ip
def is_websocket_conflict(host, port, path):
    # Check for conflicts in running WebSocket servers
    if not is_ip_in_range(host, START_IP, END_IP):
        return True
    return any(task['port'] == port or task['path'] == path for task in websocket_server_tasks.values())
def remove_popen_from_dict(d):
    #print('[remove_popen_from_dict] called')
    copy_dict = {}
    for key, value in d.items():
        if isinstance(value, dict):
            new_value = {
                k: v for k, v in value.items()
                if not (k == 'process' and isinstance(v, subprocess.Popen))
            }
            copy_dict[key] = new_value
        else:
            copy_dict[key] = value

    return copy_dict
########################-- start webSocket --#####################
async def monitor_websocket_task(id):
    # Monitor the WebSocket task for a specific game
    task = websocket_server_tasks[id]
    while not task['process'].poll():
        await asyncio.sleep(1)
    print(f"WebSocket server pid:{task['process_pid']} for game {id} has fully terminated.")
    del websocket_server_tasks[id]

# Endpoint to start the WebSocket server
async def handle_start_websocket(request):
    data = await request.json()
    game_name = data.get('game_name')
    user_nickname = data.get('user_nickname')
    file_name = data.get('file_name')
    host = data.get('host')
    port = int(data.get('port'))
    path = data.get('path')

    # Check if a WebSocket server is already running on the same port or path
    if is_websocket_conflict(host, port, path):
        return web.json_response({
            'status': 'error',
            'message': 'A WebSocket server is already running on this port or path or ip.'
        }, status=400)

    # Create and start the WebSocket server process
    cmd = [
        'python', 'servidor.py',
        '--host', host,
        '--port', str(port)
    ]
    if path is not None:
        cmd.extend(['--path', path])
    if file_name is not None:
        cmd.extend(['--file_name', file_name])

    process = subprocess.Popen(cmd)

    # Store the process and its information in the websocket_tasks dictionary
    tasks_id = str(uuid.uuid4())
    websocket_server_tasks[tasks_id] = {
        'process':process,
        'process_pid': process.pid,
        'host': host,
        'port': port,
        'path': path,
        'user_nickname':user_nickname,
        'players': 0,
        'start_time': str(datetime.now()),
        'file_name':file_name,
        'game_name':game_name
    }

    # Start monitoring the WebSocket server task
    asyncio.create_task(monitor_websocket_task(tasks_id))

    return web.json_response({
        'status': 'success',
        'message': f"WebSocket server started on {host}:{port}{path}"
    })

#---------------------------------------------------| Init server |
async def start_server():
    routes = [
        web.get('/', handle_home),  # Redirect root to /home
        web.get('/home', handle_home),  # Display index.html content
        web.get('/login', handle_login_page),  # Display login.html content
        web.get('/player', handle_player),  # Display player.html content
        web.get('/master', handle_master),  # Display master.html content
        web.get('/get_info/{key}', handle_get_info),
        web.post('/login', handle_login),
        web.post('/start_websocket', handle_start_websocket),
        web.static('/static', './static')
    ]

    # Create the application with middleware and routes
    app = web.Application(middlewares=[cors_middleware])
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    try:
        site = web.TCPSite(runner, HOST, PORT)

        print(f"Server HTTP initialized on http://{HOST}:{PORT}")
        
        await site.start()
        while SERVER_ON:
            await asyncio.sleep(1)
    except asyncio.CancelledError as ce:
        print(f"Fatal error: {ce}")
    finally:
        await runner.cleanup()
        print("Server closed.")

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("Server manually stopped with Ctrl+C.")