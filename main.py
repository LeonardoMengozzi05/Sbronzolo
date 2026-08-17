from clients import Clients
from enum import Enum, auto
from pathlib import Path
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
        stop_event.wait(30)
thread = threading.Thread(target=bouncer, daemon=True)
thread.start()

def findUserOnServer():
    return clients.get(app.storage.user.get('token'))

@ui.page('/')
async def start():
    app.add_static_files('/font', 'font')
    app.add_static_files('/img', 'img')
    ui.add_head_html('''
        <style>
            @font-face {
                font-family: 'CombatSport';
                src: url('/font/Combat Sport.otf');
            }
            *, body {
                font-family: 'CombatSport', sans-serif;
            }
        </style>
    ''')

    client = findUserOnServer()
    if not client:
        token = app.storage.user.get('token')
        if token is None:
            token = str(uuid.uuid4())
            app.storage.user['token'] = token
        client = clients.add(token)
    heartbeat = ui.timer(5.0, client.update_activity)
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
    def queue():
        if clients.isFirst(client):
            app.storage.user['state'] = State.COCKTAIL
            switch.refresh()
            return
        with ui.column().classes('w-full items-center'):
            ui.label('Sbronzolo').classes('text-5xl')
            ui.image('/img/sbronzolo.jpeg').classes('w-4/5')
            ui.label().bind_text_from(
                client, 
                'position', 
                backward=lambda position: f'Sei il {position}° in coda'
            ).classes('text-lg')
            async def wait_for_turn():
                await client.event.wait()
                app.storage.user['state'] = State.COCKTAIL
                switch.refresh()
            asyncio.create_task(wait_for_turn())
    def cocktail():
        with open('cocktails.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        def seleziona_cocktail(c):
            app.storage.user['cocktail'] = c['nome']
            app.storage.user['state'] = State.SHAKING
            switch.refresh()
        with ui.column().classes('w-full items-center'):
            ui.label('Sbronzolo').classes('text-5xl')
            ui.label('Seleziona il cocktail:').classes('text-lg')
            for c in data:
                ui.button(
                    c['nome'], 
                    on_click=lambda c=c: seleziona_cocktail(c)
                ).classes('w-3/5 text-xl bg-black')
    async def shaking():
        c = app.storage.user.get('cocktail')
        with ui.column().classes('w-full items-center'):
            ui.label('Sbronzolo').classes('text-5xl')
            ui.label(f"Il tuo {c} è in preparazione").classes('text-lg')
            spinner = ui.spinner(size='lg', color='black')
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
            app.storage.user['state'] = State.READY_TO_DRINK
            switch.refresh()
    def readyToDrink():
        with ui.column().classes('w-full items-center'):
            ui.label('Sbronzolo').classes('text-5xl')
            ui.label('Il tuo cocktail è pronto!').classes('text-lg')
            def ritirato():
                heartbeat.cancel()
                app.storage.user.pop('token', None)
                clients.logout()
                ui.run_javascript('window.close();')
            ui.button('Ritira e Esci', on_click=ritirato).classes('text-xl bg-black')

    await switch()

ui.run(
    host='0.0.0.0', 
    port=8080, 
    storage_secret='Sbronzolo',
    title='Sbronzolo',
    favicon='🍸')