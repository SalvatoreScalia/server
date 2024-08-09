import asyncio
import websockets
import json
from aiohttp import web
from aiohttp.web_middlewares import middleware
import os
from classes import EstadioPartida
from pint import UnitRegistry


######################################################
#                   Types of chips
######################################################
TYPE_CHIP = {
    # MILITARY
    'MILITARY_BUILDING': 'military building',
    'MILITARY_UNIT': 'military unit',
    'LOGISTIC_UNIT': 'logistic unit',
    'ARMOR_UNIT': 'armor unit',
    'SHIP_UNIT': 'ship unit',
    'AIR_UNIT': 'air unit',
    'AIRPORT': 'airport',
    'SHIPYARD': 'shipyard',
    'MILITARY_BASE': 'military base',
    'FORTRESS': 'fortress',
    'BUNKER': 'bunker',
    'SHOOTING_RANGE': 'shooting range',
    'RADAR_STATION': 'radar station',
    'COMMAND_AND_CONTROL_CENTER': 'command and control center',
    'MILITARY_RESEARCH_AND_DEVELOPMENT_CENTER': 'military research and development center',
    'MILITARY_TRAINING_CENTER': 'military training center',
    'AMMUNITION_STORAGE': 'ammunition storage',
    # INDUSTRIAL
    'REFINERY': 'refinery',
    'TANK_FACTORY': 'tank factory',
    'POWER_PLANT': 'power plant',
    'NUCLEAR_PLANT': 'nuclear plant',
    'SILO': 'silo',
    'WATER_TREATMENT_PLANT': 'water treatment plant',
    'WAREHOUSE': 'warehouse',
    'MANUFACTURING_PLANT': 'manufacturing plant',
    'INDUSTRIAL_ZONE': 'industrial zone',
    'RAILWAY_NETWORK': 'railway network',
    'SERVICE_STATION': 'service station',
    # CIVIL
    'BUILDING': 'building',
    'AIRPORT': 'airport',
    'PORT': 'port',
    'HOSPITAL': 'hospital',
    'SCHOOL': 'school',
    'ROAD_NETWORK': 'road network',
    'BRIDGE': 'bridge',
    'WATER_SUPPLY_SYSTEM': 'water supply system',
    'SEWAGE_SYSTEM': 'sewage system',
    'LIBRARY': 'library',
    'RESIDENTIAL_BUILDING': 'residential building',
    'COMMERCIAL_BUILDING': 'commercial building',
    'PARK': 'park',
    'PUBLIC_TRANSPORT_STATION': 'public transport station',
    'STADIUM': 'stadium',
    # INFRASTRUCTURE DE EXTRACCIÓN DE RECURSOS
    'OIL_RIG': 'oil rig',
    'OIL_FIELD': 'oil field',
    'GAS_FIELD': 'gas field',
    'MINE': 'mine',
    'COAL_MINE': 'coal mine',
    'URANIUM_MINE': 'uranium mine',
    'QUARRY': 'quarry',
    'PROCESSING_PLANT': 'processing plant',
    'EXPLORATION_SITE': 'exploration site',
    'REFINERY': 'refinery'
}
######################################################
#               QUANTITY WORLDS VALUES
######################################################
# small_well in bbl
S_W_QTY = 3e10
S_W_BASE_EXT = 1
S_W_MAX_CONST_EXT = 10

# Ruta del archivo JSON
DATA_FILE = 'data.json'
# Variable para controlar la ejecución del servidor
stop_server = False

# Función para cargar datos desde un archivo JSON
def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            datos = json.load(file)
            try:
                usuarios = datos.get('usuarios', {})
                estadios_partida = [EstadioPartida(**clase) for clase in datos.get('estadios_partida', [])]
                return usuarios, estadios_partida
            except Exception as e:
                print(e)
    return {
        'master1': {'nick':'nicknamemaster1','password': 'master1', 'role': 'admin'},
        'player1': {'nick':'nicknameplayer1','password': 'player1', 'role': 'player'},
        'player2':{'nick':'nicknamemplayer2','password': 'player2','role':'player'}
    }, [EstadioPartida(True)]

# Función para guardar datos en un archivo JSON
def guardar_datos():
    with open(DATA_FILE, 'w') as file:
        json.dump({
            'usuarios': usuarios,
            'estadios_partida': [clase.to_dic() for clase in estadios_partida]
        }, file, indent=4)

# Cargar usuarios y clases desde el archivo JSON al iniciar
usuarios, estadios_partida = cargar_datos()

# Middleware para permitir CORS
@middleware
async def cors_middleware(request, handler):
    if request.method == 'OPTIONS':
        # Respuesta a la solicitud OPTIONS
        response = web.Response(status=200)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    else:
        # Respuesta a solicitudes reales
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

# Manejar solicitudes de login
async def handle_login(request):
    try:
        data = await request.json()
        username = data.get('username')
        password = data.get('password')

        user = usuarios.get(username)
        if user and user['password'] == password:
            return web.json_response({'status': 'success', 'role': user['role']})
        else:
            return web.json_response({'status': 'error'}, status=401)
    except json.JSONDecodeError:
        return web.json_response({'status': 'error', 'message': 'Invalid JSON'}, status=400)

# Enviar el estado de las partida a los clientes
async def enviar_estado(websocket, path):
    global stop_server
    global estadios_partida
    try:
        while not stop_server:
            for estadio in estadios_partida:
                estadio.update_state_datetime()
                print([estadio.to_dic() for estadio in estadios_partida])
            message = json.dumps([estadio.to_dic() for estadio in estadios_partida])
            await websocket.send(message)
            await asyncio.sleep(0.1)
    except websockets.ConnectionClosed:
        print("Conexión cerrada con el cliente.")

# Recibir y manejar comandos
async def recibir_comandos(websocket, path):
    global stop_server
    async for message in websocket:
        try:
            comando = json.loads(message)
            if comando == "stop":
                print("Comando 'stop' recibido. Guardando estado y deteniendo servidor.")
                for estadio in estadios_partida:
                    estadio.save_state()
                guardar_datos()  # Guardar datos al detener el servidor
                stop_server = True
                break
            else:
                index = comando.get("index")
                new_state = comando.get("state")
                for i, estadio in enumerate(estadios_partida):
                    if i == index:
                        estadio.data_state = new_state
                        estadios_partida.insert(index,EstadioPartida(True))
                        print(f"Modificado el estadio {index} data_state actualizado a: {new_state}")
                        guardar_datos()  # Guardar datos después de actualizar
                        break
        except json.JSONDecodeError:
            print("Error al decodificar el comando.")

# Iniciar el servidor
async def start_server():
    global stop_server
    # Configuración del servidor HTTP (login)
    app = web.Application(middlewares=[cors_middleware])
    app.router.add_post('/login', handle_login)
    
    # Configuración de WebSockets
    estado_server = await websockets.serve(enviar_estado, "localhost", 8765)
    comando_server = await websockets.serve(recibir_comandos, "localhost", 8766)

    # Iniciar el servidor HTTP
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()

    print("Servidor WebSocket iniciado en ws://localhost:8765")
    print("Servidor de comandos iniciado en ws://localhost:8766")
    print("Servidor HTTP para login iniciado en http://localhost:8080")

    try:
        while not stop_server:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Servidor detenido manualmente.")
    finally:
        estado_server.close()
        await estado_server.wait_closed()
        comando_server.close()
        await comando_server.wait_closed()
        print("Servidor cerrado.")

if __name__ == "__main__":
    asyncio.run(start_server())
