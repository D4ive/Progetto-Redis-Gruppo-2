import redis
import json
import time
import database as db
from auth import login_utente, registra_utente

r = db.connection()

print("--- PRODUTTORE DI NOTIFICHE ---")
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

if ruolo != "produttore":
    print("Accesso non autorizzato. Solo i produttori possono inviare notifiche.")
    exit()

while True:
    canale = input("\nCanale (es. sport.calcio): ").strip()
    titolo = input("Titolo: ").strip()
    messaggio = input("Messaggio: ").strip()

    notifica = {
        "titolo": titolo,
        "messaggio": messaggio,
        "timestamp": time.time(),
        "autore": username
    }

    r.publish(canale, json.dumps(notifica))
    r.rpush(f"notifiche:{canale}", json.dumps(notifica))
    r.expire(f"notifiche:{canale}", 3600 * 6)
    print(f"Notifica inviata su '{canale}'")
