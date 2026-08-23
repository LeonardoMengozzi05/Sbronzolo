from multiprocessing.connection import Client
from contextlib import contextmanager
from nicegui import app, ui
from classes.clients import Clients
from enum import Enum, auto
import multiprocessing
import uuid
import asyncio
import json

app.add_static_files('/font', 'font')
app.add_static_files('/img', 'img')

multiprocessing.current_process().authkey = b'SbronZolo67!'

class State(Enum):
    CODA = auto()
    COCKTAIL = auto()
    SHAKING = auto()
    COMPLEATE = auto()
    READY_TO_DRINK = auto()
    BYE = auto()

clients = Clients()

async def bouncer_task():
    while True:
        try:
            clients.removeSlogged()
        except Exception as e:
            print(f"Errore bouncer: {e}")
        await asyncio.sleep(3)
app.on_startup(lambda: asyncio.create_task(bouncer_task()))

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
    def switch():
        match app.storage.user['state']:
            case State.CODA:
                queue()
            case State.COCKTAIL:
                cocktail()
            case State.SHAKING:
                shaking()
            case State.COMPLEATE:
                compleate()
            case State.READY_TO_DRINK:
                readyToDrink()
            case State.BYE:
                bye()
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
        with open('jsons/cocktails.json', 'r', encoding='utf-8') as file:
            COCKTAILS_DATA = json.load(file)
        def seleziona_cocktail(c):
            app.storage.user['cocktail'] = c
            switchTo(State.SHAKING)
        with layout():
            ui.label('E il tuo turno\nSeleziona il cocktail').classes('text-xl text-center whitespace-pre-line')
            for c in COCKTAILS_DATA:
                if c['disponibile']:
                    ui.button(
                        c['nome'], 
                        on_click=lambda c=c: seleziona_cocktail(c)
                    ).classes('w-3/5 text-lg bg-black')
    def shaking():
        c = app.storage.user.get('cocktail', {})
        with layout():
            ui.label(f'Il tuo {c['nome']}\nè in preparazione!').classes('text-xl text-center whitespace-pre-line')
            spinner = ui.spinner(size='lg', color='black')
            async def prepare():
                try:
                    with Client(('localhost', 6000)) as conn:
                        conn.send({"cocktail": c})
                        conn.recv()
                        switchTo(State.COMPLEATE)
                except Exception as e:
                    pass
            task = asyncio.create_task(prepare())
            ui.context.client.on_disconnect(task.cancel)
    def compleate():
        c = app.storage.user.get('cocktail', {})
        toppings = [ing["nome"] for ing in c["ingredienti"] if ing["quantita"] == 'full']
        if not len(toppings):
            switchTo(State.READY_TO_DRINK)
        with layout():
            ui.label(f'Il to {c['nome']}\nè guasi pronto! Aggiungi:').classes('text-xl text-center whitespace-pre-line')
            for topping in toppings:
                ui.label(topping).classes('text-xl')
            ui.button('Fatto', on_click=lambda: switchTo(State.READY_TO_DRINK)).classes('text-lg bg-black')
    def readyToDrink():
        with layout():
            ui.label('Il tuo cocktail è pronto!').classes('text-xl')
            def ritirato():
                heartbeat.cancel()
                app.storage.user.pop('token', None)
                clients.logout()
                switchTo(State.BYE)
            ui.button('Ritira', on_click=ritirato).classes('text-lg bg-black')
    def bye():
        with layout():
            ui.image('/img/byebye.jpeg').classes('w-4/5')
            ui.label('Puoi chiudere questa pagina\nArrivederci!').classes('text-xl text-center whitespace-pre-line')
    switch()

ui.run(
    host='0.0.0.0', 
    port=8080, 
    storage_secret='Sbronzolo',
    title='Sbronzolo',
    favicon='🍸'
)