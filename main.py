from clients import Clients
import threading
from datetime import datetime
from functools import wraps
from nicegui import app, ui
import uuid
import asyncio
import json

# http://lm.local:8080

clients = Clients()

stop_event = threading.Event()
def bouncer():
    while not stop_event.is_set():
        clients.removeSlogged()
        stop_event.wait(30)
app.on_shutdown(lambda: stop_event.set())
thread = threading.Thread(target=bouncer, daemon=True)
thread.start()

def findUserOnServer():
    return clients.get(app.storage.user.get('token'))

def richiede_client_valido(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        client = findUserOnServer()
        if not client:
            app.storage.user.pop('token', None)
            ui.notify("Sessione non valida o scaduta.", type='warning')
            ui.navigate.to('/')
            return
        if not clients.isFirst(client):
            ui.notify("Stai saltando la fila furbetto.", type='warning')
            ui.navigate.to('/')
            return
        ui.timer(10.0, lambda: client.update_activity)
    return wrapper

@ui.page('/')
async def start():
    client = findUserOnServer()
    if not client:
        token = app.storage.user.get('token')
        if token is None:
            token = str(uuid.uuid4())
            app.storage.user['token'] = token
        client = clients.add(token)
    ui.timer(10.0, lambda: client.update_activity())
    if clients.isFirst(client):
        ui.navigate.to('/cocktail')
        return
    ui.label().bind_text_from(client, 'position', backward=lambda position: f'Posizione: {position}')
    async def wait_for_turn():
        await client.event.wait()
        ui.navigate.to('/cocktail')
    asyncio.create_task(wait_for_turn())

@ui.page('/cocktail')
@richiede_client_valido
async def cocktail():
    with open('cocktails.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    ui.label('Seleziona il cocktail:')
    def seleziona_cocktail(c):
        app.storage.user['cocktail'] = c['nome']
        ui.navigate.to('/shaking')
    for c in data:
        ui.button(c['nome'], on_click=lambda c=c: seleziona_cocktail(c))

@ui.page('/shaking')
@richiede_client_valido
async def shaking():
    c = app.storage.user.get('cocktail')
    if c is not None:
        ui.label(f"Sbronzolo sta preparando il tuo {c['nome']}")
        spinner = ui.spinner()
        spinner.visible = True

        # process = await asyncio.create_subprocess_exec(
        #     'python3',
        #     'gpio_program.py',
        #     stdout=asyncio.subprocess.PIPE,
        #     stderr=asyncio.subprocess.PIPE,
        # )
        #stdout, stderr = await process.communicate()
        #risultato = stdout.decode().strip()

        await asyncio.sleep(15)

        spinner.visible = False
        ui.navigate.to('/readyToDrink')
    else:
        ui.notify("C'è stato un errore. Riprova.", type='warning')
        ui.navigate.to('/')

@ui.page('/readyToDrink')
@richiede_client_valido
def readyToDrink():
    ui.label('FINE')
    clients.logout()
    app.storage.user.pop('token', None)

ui.run(host='0.0.0.0', port=8080, storage_secret='stronzo')