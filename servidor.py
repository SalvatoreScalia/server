import asyncio
import websockets
import json
from aiohttp import web
from aiohttp.web_middlewares import middleware
from controller import guardar_datos, cargar_datos, EstadioPartida, dateTimeLib

# Variable para controlar la ejecución del servidor
stop_server = False
#current_user
user = {}

# Función para configurar los headers CORS
def configure_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Accept'
    return response


# Middleware para permitir CORS
@middleware
async def cors_middleware(request, handler):
    if request.method == 'OPTIONS':
        response = web.Response(status=200)
        return configure_cors_headers(response)
    else:
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


# Manejar solicitudes de login
async def handle_login(request):
    global user
    try:
        data = await request.json()
        username = data.get('username')
        password = data.get('password')
        user = usuarios.get(username)
        print(f"{user['nick']} ha enetrado en la partida.")
        if user and user['password'] == password:
            user['status'] = f'last-login: {dateTimeLib.now().strftime("%Y-%m-%d %H:%M:%S")}'
            return web.json_response({'status': 'success','role': user['role']})
        else:
            return web.json_response({'status': 'error'}, status=401)
    except json.JSONDecodeError:
        return web.json_response({'status': 'error','message': 'Invalid JSON'},status=400)

# Enviar el estado de las partidas a los clientes
async def enviar_estado(websocket, path):
    global stop_server
    try:
        while not stop_server:
            message = json.dumps([estadio.to_dict() for estadio in estadios_partida])
            await websocket.send(message)
            await asyncio.sleep(0.1)
    except websockets.ConnectionClosed as wscc:
        print(f"Conexión cerrada con el cliente: {wscc}")
    finally:
        print('fin enviar_estado')


# Recibir y manejar comandos
async def recibir_comandos(websocket, path):
    global stop_server
    try:
        async for message in websocket:
            try:
                dict = json.loads(message)
                if dict == "stop":
                    print("Comando 'stop' recibido. Guardando estado y deteniendo servidor.")
                    for estadio in estadios_partida:#imprimir que se esta guardando
                        estadio.save_state()
                    guardar_datos(usuarios, estadios_partida)  # Guardar datos al detener el servidor
                    stop_server = True
                    break
                else:
                    index = dict.get("index")
                    new_state = dict.get("state")
                    for i, estadio in enumerate(estadios_partida):
                        if i == index:
                            estadio.update_state_datetime()
                            estadio.data_state = False
                            estadios_partida.insert(index,EstadioPartida(creator_player=user,data_state=new_state,state='Nueva imagen de partida añadida.'))
                            print(f"Modificado el estadio [{index}] data_state actualizado a: {estadio.data_state}")
                            guardar_datos(usuarios=usuarios,estadios_partida=estadios_partida)  # Guardar datos después de actualizar
                            break
            except json.JSONDecodeError:
                print("Error al decodificar el comando del JSON.")
            except Exception as e:
                print(f"Error: {e}")
    except websockets.ConnectionClosed as wscc:
        print(f"Conexión cerrada con el cliente: {wscc}")
    finally:
        print('fin recibir_comandos')


# Iniciar el servidor
async def start_server():
    global stop_server
    # Configuración del servidor HTTP (login)
    app = web.Application(middlewares=[cors_middleware])
    app.router.add_post('/login', handle_login)
    #app.router.add_route('OPTIONS', '/login', handle_options)

    # Configuración de WebSockets
    data_server = await websockets.serve(enviar_estado, "0.0.0.0", 3001)
    command_server = await websockets.serve(recibir_comandos, "0.0.0.0", 3002)

    # Iniciar el servidor HTTP
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', 8080)
    await site.start()

    print("Servidor WebSocket dataIncoming iniciado en wss://0.0.0.0:3001")
    print("Servidor WebSocket commands iniciado en wss://0.0.0.0:3002")
    print("Servidor HTTP para login iniciado en http://127.0.0.1:8080")

    try:
        while not stop_server:
            await asyncio.sleep(1)
    except asyncio.CancelledError as ce:
        print(f"Servidor detenido: {ce}")
    finally:
        data_server.close()
        command_server.close()
        await data_server.wait_closed()
        await command_server.wait_closed()
        await runner.cleanup()
        print("Servidor cerrado.")


if __name__ == "__main__":
    usuarios, estadios_partida = cargar_datos()
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("Servidor detenido manualmente Ctrl^C.")
