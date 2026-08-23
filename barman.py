from multiprocessing.connection import Listener
from classes.alcol import Alcols
import multiprocessing
import signal
import time

def mixing(cocktail):
    for ing in cocktail["ingredienti"]:
        alcol = alcols.getAlcolByName(ing['nome'])
        if alcol:
            alcol.dispense(ing['quantita'])
            time.sleep(0.001)

def loop():
    while True:
        try:
            conn = listener.accept()
            cocktail = conn.recv().get('cocktail')
            mixing(cocktail)
            conn.send({"status": "finito"})
            conn.close()
        except (OSError, EOFError):
            break

def handleClosing(signum, frame):
    if alcols and hasattr(alcols, 'stopAll'):
        alcols.stopAll()
    if listener:
        try:
            listener.close()
        except Exception:
            pass

# Intercetta sia Ctrl+C (SIGINT) che il comando kill standard (SIGTERM)
signal.signal(signal.SIGINT, handleClosing)
signal.signal(signal.SIGTERM, handleClosing)

print("Barman ready")
multiprocessing.current_process().authkey = b'SbronZolo67!'
listener = Listener(('0.0.0.0', 6000))
alcols = Alcols()

try:
    loop()
finally:
    if listener:
        listener.close()
