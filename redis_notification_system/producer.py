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

    notifica = db.crea_notifica(canale, notifica)
    if notifica: print(f"Notifica inviata su '{canale}'")