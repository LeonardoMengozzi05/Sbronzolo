from gpiozero import OutputDevice
import time

class plump():
    def __init__(self):
        pass
    def operate(self, time):

        # Pin BCM collegato al Gate del MOSFET
        # initial_value=False garantisce che la pompa sia SPENTA all'avvio
        pompa = OutputDevice(18, active_high=True, initial_value=False)

        print("Accensione pompa...")
        pompa.on()          # Mette il pin a HIGH (3.3V) -> MOSFET conduce
        time.sleep(3)       # Eroga per 3 secondi

        print("Spegnimento pompa...")
        pompa.off()         # Mette il pin a LOW (0V) -> MOSFET si blocca