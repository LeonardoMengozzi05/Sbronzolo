from clients import Clients
from enum import Enum, auto
from pathlib import Path
from functools import wraps
from nicegui import app, ui
import uuid
import threading
import asyncio
import json

class State(Enum):
    CODA = auto()
    COCKTAIL = auto()
    SHAKING = auto()
    READY_TO_DRINK = auto()
    BYE = auto()

clients = Clients()

stop_event = threading.Event()
app.on_shutdown(stop_event.set)
def bouncer():
    while not stop_event.is_set():
        clients.removeSlogged()
        stop_event.wait(10)
thread = threading.Thread(target=bouncer, daemon=True)
thread.start()

def findUserOnServer():
    return clients.get(app.storage.user.get('token'))

@ui.page('/')
async def start():
    client = findUserOnServer()
    if not client:
        token = app.storage.user.get('token')
        if token is None:
            token = str(uuid.uuid4())
            app.storage.user['token'] = token
        client = clients.add(token)
    ui.timer(2.0, client.update_activity)
    app.storage.user['state'] = State.CODA

    @ui.refreshable
    async def switch():
        match app.storage.user['state']:
            case State.CODA:
                queue()
            case State.COCKTAIL:
                cocktail()
            case State.SHAKING:
                await shaking()
            case State.READY_TO_DRINK:
                readyToDrink()
            case State.BYE:
                bye()
    def queue():
        client = findUserOnServer()
        if clients.isFirst(client):
            app.storage.user['state'] = State.COCKTAIL
            switch.refresh()
            return
        ui.label().bind_text_from(
            client, 
            'position', 
            backward=lambda position: f'Posizione: {position}'
        )
        async def wait_for_turn():
            if client is not None:
                await client.event.wait()
                app.storage.user['state'] = State.COCKTAIL
                switch.refresh()
        asyncio.create_task(wait_for_turn())
    def cocktail():
        with open('cocktails.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        ui.label('Seleziona il cocktail:')
        def seleziona_cocktail(c):
            app.storage.user['cocktail'] = c['nome']
            app.storage.user['state'] = State.SHAKING
            switch.refresh()
        for c in data:
            ui.button(c['nome'], on_click=lambda c=c: seleziona_cocktail(c))
    async def shaking():
        c = app.storage.user.get('cocktail')
        if c is not None:
            ui.label(f"Sbronzolo sta preparando il tuo {c}")
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

            #await asyncio.sleep(15)

            spinner.visible = False
            app.storage.user['state'] = State.READY_TO_DRINK
            switch.refresh()
        else:
            ui.notify("C'è stato un errore. Riprova.", type='warning')
            ui.navigate.to('/')
    def readyToDrink():
        ui.label('Il tuo cocktail è pronto. Ritiralo e premi il seguente bottone.')
        def ritirato():
            clients.logout()
            app.storage.user.pop('token', None)
            app.storage.user['state'] = State.BYE
            switch.refresh()
        ui.button('Ritirato', on_click=ritirato)
    def bye():
        ui.image(Path('img/sbronzolo.jpeg')).classes('w-64')

    await switch()

ui.run(host='0.0.0.0', port=8080, storage_secret='stronzo')