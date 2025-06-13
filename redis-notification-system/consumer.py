import redis
import json
import threading
import time
import utils
from auth import login_utente, registra_utente

r = utils.connection()

print("--- CONSUMATORE DI NOTIFICHE ---")
scelta = input("1. Registrati\n2. Login\nScegli un'opzione: ").strip()
if scelta == "1":
    risultato = registra_utente()
    if risultato is None:
        exit()
    username, ruolo = risultato
elif scelta == "2":
    username, ruolo = login_utente()
    if ruolo is None:
        exit()
else:
    print("Scelta non valida.")
    exit()

if ruolo != "consumatore":
    print("Accesso non autorizzato. Solo i consumatori possono ricevere notifiche.")
    exit()

key_sottoscrizioni = f"sottoscrizioni:{username}"
if not r.exists(key_sottoscrizioni):
    print("\nNessun canale sottoscritto.")
    print("Esempi: sport, sport.calcio, tecnologia, finanza")
    canali = input("Inserisci i canali separati da virgola: ").split(',')
    for c in canali:
        r.sadd(key_sottoscrizioni, c.strip())
    print("Canali sottoscritti salvati.")

canali = list(r.smembers(key_sottoscrizioni))
print(f"\nSottoscritto ai canali: {canali}")

# mostra ultime notifiche
for c in canali:
    recenti = r.lrange(f"notifiche:{c}", -5, -1)
    for raw in recenti:
        dati = json.loads(raw)
        print(f"[{c}] {dati['titolo']} - {dati['messaggio']} (da {dati.get('autore', 'sconosciuto')})")

pubsub = r.pubsub()
pubsub.subscribe(*canali)

def ascolta():
    for msg in pubsub.listen():
        if msg['type'] == 'message':
            dati = json.loads(msg['data'])
            canale = msg['channel']
            print(f"\n📩 [{canale}] {dati['titolo']}: {dati['messaggio']} (da {dati.get('autore', 'sconosciuto')})")

threading.Thread(target=ascolta, daemon=True).start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nUscita.")
