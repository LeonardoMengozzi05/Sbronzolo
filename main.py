from nicegui import app, ui
from contextlib import contextmanager
from clients import Clients
from enum import Enum, auto
import uuid
import threading
import asyncio
import json

app.add_static_files('/font', 'font')
app.add_static_files('/img', 'img')

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
        stop_event.wait(5)
thread = threading.Thread(target=bouncer, daemon=True)
thread.start()

@ui.page('/')
async def home():
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

    token = app.storage.user.get('token')
    if token is None:
        token = str(uuid.uuid4())
        app.storage.user['token'] = token
    client = clients.get(token)
    if not client:
        client = clients.add(token)

    heartbeat = ui.timer(2.0, client.update_activity)

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
    def switchTo(next):
        try:
            if not client or not client.isLogged():
                return
            app.storage.user['state'] = next
            switch.refresh()
        except (RuntimeError, KeyError, AssertionError):
            pass
    @contextmanager
    def layout():
        with ui.column().classes('w-full items-center'):
            ui.label('Sbronzolo').classes('text-5xl mb-16')
            yield
    def queue():
        if clients.isFirst(client):
            switchTo(State.COCKTAIL)
            return
        with layout():
            ui.image('/img/sbronzolo.jpeg').classes('w-4/5')
            ui.label().bind_text_from(
                client, 
                'position', 
                backward=lambda position: f'Sei il {position}° in coda'
            ).classes('text-lg')
            async def wait_for_turn():
                await client.event.wait()
                switchTo(State.COCKTAIL)
            task = asyncio.create_task(wait_for_turn())
            ui.context.client.on_disconnect(task.cancel)
    def cocktail():
        with open('cocktails.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        def seleziona_cocktail(c):
            app.storage.user['cocktail'] = c['nome']
            switchTo(State.SHAKING)
        with layout():
            ui.label('E il tuo turno\nSeleziona il cocktail').classes('text-xl text-center whitespace-pre-line')
            for c in data:
                ui.button(
                    c['nome'], 
                    on_click=lambda c=c: seleziona_cocktail(c)
                ).classes('w-3/5 text-lg bg-black')
    async def shaking():
        c = app.storage.user.get('cocktail')
        with layout():
            ui.label(f'Il tuo {c}\nè in preparazione').classes('text-xl text-center whitespace-pre-line')
            spinner = ui.spinner(size='lg', color='black')
            # process = await asyncio.create_subprocess_exec(
            #     'python3',
            #     'gpio_program.py',
            #     stdout=asyncio.subprocess.PIPE,
            #     stderr=asyncio.subprocess.PIPE,
            # ) 
            #stdout, stderr = await process.communicate()
            #risultato = stdout.decode().strip()
            try:
                await asyncio.sleep(15)
                switchTo(State.READY_TO_DRINK)
            except asyncio.CancelledError:
                pass
    def readyToDrink():
        with layout():
            ui.label('Il tuo cocktail è pronto!').classes('text-xl')
            def ritirato():
                heartbeat.cancel()
                app.storage.user.pop('token', None)
                clients.logout()
                ui.run_javascript('window.close();')
            ui.button('Ritira e Esci', on_click=ritirato).classes('text-lg bg-black')

    await switch()

ui.run(
    host='0.0.0.0', 
    port=8080, 
    storage_secret='Sbronzolo',
    title='Sbronzolo',
    favicon='🍸'
)