from gpiozero import OutputDevice, Button
import json
from signal import pause

with open('../data/jsons/alcols.json', "r", encoding="utf-8") as file:
    alcos = json.load(file)

dispositivi = []

for alcol in alcos:
    pompa = OutputDevice(
        alcol['pompa'], 
        active_high=True, 
        initial_value=False
    )
    bottone = Button(alcol['bottone'])
    
    bottone.when_pressed = lambda p=pompa: p.on()
    bottone.when_released = lambda p=pompa: p.off()
    
    dispositivi.append({
        'pompa': pompa, 
        'bottone': bottone
    })

print("Sistema pronto! Premere CTRL+C per terminare.")

pause()
