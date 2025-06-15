import json
import threading
import time
import database as db
from auth import login_utente, registra_utente

r = db.connection()

# Menu con gestione errori
while True:
    print("--- CONSUMATORE DI NOTIFICHE ---")
    scelta = input("1. Registrati\n2. Login\nScegli un'opzione: ").strip()
    
    if scelta == "1":
        risultato = registra_utente("consumatore")
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

if ruolo != "consumatore":
    print("Accesso non autorizzato. Solo i consumatori possono ricevere notifiche.")
    exit()

# Menu gestione canali
while True:
    print("\n--- MENU CONSUMATORE ---")
    print("1. Visualizza canali a cui sei iscritto")
    print("2. Visualizza canali disponibili")
    print("3. Iscriviti a un canale")
    print("4. Disiscriviti da un canale")
    print("5. Inizia ad ascoltare notifiche")
    
    scelta = input("Scegli un'opzione: ").strip()
    
    if scelta == "1":
        # Mostra canali iscritto
        canali_iscritto = db.ottieni_canali_utente(username)
        if canali_iscritto:
            print(f"Canali iscritto: {canali_iscritto}")
        else:
            print("Non sei iscritto a nessun canale.")
    
    elif scelta == "2":
        # Mostra canali disponibili
        canali_disponibili = db.ottieni_canali_disponibili()
        if canali_disponibili:
            print(f"Canali disponibili: {canali_disponibili}")
        else:
            print("Nessun canale disponibile.")
    
    elif scelta == "3":
        # Iscriviti a canale
        canali_disponibili = db.ottieni_canali_disponibili()
        print(f"Canali disponibili: {canali_disponibili}")
        canale = input("Canale a cui iscriversi: ").strip()
        if db.iscriviti_canale(username, canale):
            print(f"Iscritto a '{canale}'.")
        else:
            print("Canale non esistente o già iscritto.")
    
    elif scelta == "4":
        # Disiscriviti da canale
        canali_iscritto = db.ottieni_canali_utente(username)
        print(f"Canali iscritto: {canali_iscritto}")
        canale = input("Canale da cui disiscriversi: ").strip()
        if db.disiscriviti_canale(username, canale):
            print(f"Disiscritto da '{canale}'.")
        else:
            print("Non sei iscritto a questo canale.")
    
    elif scelta == "5":
        # Inizia ascolto (logica originale modificata)
        key_sottoscrizioni = f"sottoscrizioni:{username}"
        
        # Se non ha sottoscrizioni, chiede di inserirle
        if not r.exists(key_sottoscrizioni):
            print("\nNessun canale sottoscritto.")
            print("Canali disponibili:", db.ottieni_canali_disponibili())
            canali_input = input("Inserisci i canali separati da virgola: ").split(',')
            for c in canali_input:
                c = c.strip()
                if c in db.ottieni_canali_disponibili():
                    r.sadd(key_sottoscrizioni, c)
            print("Canali sottoscritti salvati.")

        canali = list(r.smembers(key_sottoscrizioni))
        if not canali:
            print("Nessun canale valido sottoscritto.")
            continue
            
        print(f"\nSottoscritto ai canali: {canali}")

        # mostra ultime notifiche
        for c in canali:
            recenti = r.lrange(f"notifiche:{c}", -5, -1)
            for raw in recenti:
                try:
                    dati = json.loads(raw)
                    print(f"[{c}] {dati['titolo']} - {dati['messaggio']} (da {dati.get('autore', 'sconosciuto')})")
                except:
                    pass

        pubsub = r.pubsub()
        pubsub.subscribe(*canali)

        def ascolta():
            for msg in pubsub.listen():
                if msg['type'] == 'message':
                    try:
                        dati = json.loads(msg['data'])
                        canale = msg['channel']

                        timestamp = dati.get('timestamp')
                        if timestamp:
                            ora_attuale = time.time()
                            secondi_passati = ora_attuale - timestamp
                            ore = int(secondi_passati // 3600)
                            minuti = int((secondi_passati % 3600) // 60)
                            if ore > 0:
                                tempo_fa = f"{ore}h fa"
                            elif minuti > 0:
                                tempo_fa = f"{minuti}m fa"
                            else:
                                tempo_fa = "ora"

                        print(f"\n📩 [{canale}] {dati['titolo']}: {dati['messaggio']} (da {dati.get('autore', 'sconosciuto')}, {tempo_fa})")
                    except:
                        pass

        threading.Thread(target=ascolta, daemon=True).start()

        try:
            print("Ascolto notifiche... (Ctrl+C per tornare al menu)")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nTornato al menu.")
            pubsub.close()
    
    else:
        print("Scelta non valida.")