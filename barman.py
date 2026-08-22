from multiprocessing.connection import Listener
from classes.alcol import Alcols
import time


def mixing(cocktail):
    for ing in cocktail["ingredienti"]:
        alcol = alcols.getAlcolByName(ing['nome'])
        if alcol:
            alcol.dispense(ing['quantita'])
            time.sleep(0.001)

def loop():
    while True:
        conn = listener.accept()
        mixing(conn.recv().get('cocktail'))
        conn.close()

try:
    ADDRESS = ('0.0.0.0', 6000)
    AUTH_KEY = b'''
        Beh, Shinji, io non posso fare altro che stare qui ad annaffiare. Pero', 
        quanto a te, quanto a quel che non puoi far che tu, per te qualcosa da 
        poter far dovrebbe esserci. Ma non ti costringera' nessuno, pensa da te 
        stesso, decidi da te stesso che cosa tu stesso possa fare. Beh, che tu 
        non abbia rammarichi.
    '''
    listener = Listener(ADDRESS, family='AF_INET', authkey=AUTH_KEY)
    alcols = Alcols()
    loop()
finally:
    listener.close()