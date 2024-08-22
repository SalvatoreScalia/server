import asyncio
import json
from aiohttp import web
from aiohttp.web_middlewares import middleware
from servidor import start_websocket
from controller import read_json_data , dateTimeLib

SERVER_ON = True
websocket_started = False  # Controla si el WebSocket ya ha sido iniciado
users , list_gs = read_json_data()

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
        response = web.Response(status=200)
        return configure_cors_headers(response)
    else:
        response = await handler(request)
        return configure_cors_headers(response)

#init of root in static and go to index.html
async def handle_root(request):
    # Redirige a /static/index.html
    raise web.HTTPFound('/static/index.html')

# Management of login
async def handle_login(request):
    try:
        data = await request.json()
        username_key = data.get('username')
        unencrypted_password = data.get('password')
        user = users.get(username_key)
        if user and user['password'] == unencrypted_password:
            print(f"{user['nick_name']} has entered the game.")
            user['status'] = f'last-login: {dateTimeLib.now().strftime("%Y-%m-%d %H:%M:%S")}'
            return web.json_response({
                'role': user['role'],
                'user_id': user['user_id'],
                'nick': user['user_nickname'],
                'competitor_id': user['competitor_id']
            })
        else:
            return web.json_response({'status': 'error'}, status=401)
    except json.JSONDecodeError:
        return web.json_response({'status': 'error', 'message': 'Invalid JSON'}, status=400)

# Endpoint to start the WebSocket server
async def handle_start_websocket(request):
    global websocket_started
    if not websocket_started:
        asyncio.create_task(start_websocket(users=users,list_game_stages=list_gs))
        websocket_started = True
        return web.json_response({'status': 'success', 'message': 'WebSocket server started.'})
    else:
        return web.json_response({'status': 'error', 'message': 'WebSocket server is already running.'})

# Init server
async def start_server():
    
    app = web.Application(middlewares=[cors_middleware])
    app.router.add_post('/login', handle_login)
    app.router.add_post('/start_websocket', handle_start_websocket)
    app.router.add_get('/', handle_root)
    app.router.add_static('/static', './static')

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', 8080)
    
    print("Server HTTP for login initialized on http://127.0.0.1:8080")
    try:        
        await site.start()
        while SERVER_ON:  
            await asyncio.sleep(20)
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