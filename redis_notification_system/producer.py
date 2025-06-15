import json
import time
import database as db
from auth import login_utente, registra_utente

r = db.connection()

# Menu con gestione errori
while True:
    print("--- PRODUTTORE DI NOTIFICHE ---")
    scelta = input("1. Registrati\n2. Login\nScegli un'opzione: ").strip()
    
    if scelta == "1":
        risultato = registra_utente("produttore")
        if risultato is None:
            continue  # Torna al menu invece di exit
        username, ruolo = risultato
        break
    elif scelta == "2":
        username, ruolo = login_utente()
        if ruolo is None:
            continue  # Torna al menu invece di exit
        break
    else:
        print("Scelta non valida. Riprova.")
        continue  # Continua il loop invece di exit

if ruolo != "produttore":
    print("Accesso non autorizzato. Solo i produttori possono inviare notifiche.")
    exit()

# Menu produttore
while True:
    print("\n--- MENU PRODUTTORE ---")
    print("1. Crea nuovo canale")
    print("2. Invia notifica")
    scelta = input("Scegli un'opzione: ").strip()
    
    if scelta == "1":
        # Crea nuovo canale
        print("\nCanali esistenti:", db.ottieni_canali_disponibili())
        nuovo_canale = input("Nome nuovo canale: ").strip()
        if nuovo_canale:
            if nuovo_canale not in db.ottieni_canali_disponibili():
                db.aggiungi_canali([nuovo_canale])
                print(f"Canale '{nuovo_canale}' creato.")
            else:
                print("Canale già esistente.")
        
    elif scelta == "2":
        # Invia notifica (logica originale)
        print("\nCanali disponibili:", db.ottieni_canali_disponibili())
        canale = input("Canale (es. sport.calcio): ").strip()
        titolo = input("Titolo: ").strip()
        messaggio = input("Messaggio: ").strip()

        notifica = {
            "titolo": titolo,
            "messaggio": messaggio,
            "timestamp": time.time(),
            "autore": username
        }

        db.aggiungi_canali([canale])
        r.publish(canale, json.dumps(notifica))
        r.rpush(f"notifiche:{canale}", json.dumps(notifica))
        r.expire(f"notifiche:{canale}", 3600 * 24)
        print(f"Notifica inviata su '{canale}'")
    
    else:
        print("Scelta non valida.")