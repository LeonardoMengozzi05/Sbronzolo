from multiprocessing.connection import Listener
import multiprocessing
from classes.alcol import Alcols
import time

multiprocessing.current_process().authkey = b'SbronZolo67!'

def mixing(cocktail):
    for ing in cocktail["ingredienti"]:
        alcol = alcols.getAlcolByName(ing['nome'])
        if alcol:
            alcol.dispense(ing['quantita'])
            time.sleep(0.001)

def loop():
    while True:
        conn = listener.accept()
        cocktail = conn.recv().get('cocktail')
        mixing(cocktail)
        conn.send({"status": "finito"})
        conn.close()

print("Barman ready")
try:
    listener = Listener(('0.0.0.0', 6000))
    alcols = Alcols()
    loop()
finally:
    listener.close()