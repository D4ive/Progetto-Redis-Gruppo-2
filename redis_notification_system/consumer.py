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
            print(f"\n📋 Canali a cui sei iscritto:")
            for canale in canali_iscritto:
                print(f"  • {canale}")
            
            # Mostra anche cosa riceverà effettivamente
            canali_ascolto = db.ottieni_canali_ascolto(username)
            sottocategorie = [c for c in canali_ascolto if c not in canali_iscritto]
            if sottocategorie:
                print(f"\n📺 Riceverai anche notifiche da queste sottocategorie:")
                for canale in sottocategorie:
                    print(f"  └── {canale}")
        else:
            print("❌ Non sei iscritto a nessun canale.")
    
    elif scelta == "2":
        # Mostra canali disponibili
        print("\n📺 Canali disponibili:")
        print(db.mostra_canali_gerarchici())
        print("\n💡 Iscrivendoti a 'sport' riceverai anche notifiche da 'sport.calcio', 'sport.tennis', ecc.")
    
    elif scelta == "3":
        # Iscriviti a canale
        print("\n📺 Canali disponibili:")
        print(db.mostra_canali_gerarchici())
        canale = input("\nCanale a cui iscriversi: ").strip()
        if db.iscriviti_canale(username, canale):
            print(f"✅ Iscritto a '{canale}'.")
            
            # Mostra sottocategorie che riceverà
            canali_ascolto = db.ottieni_canali_ascolto(username)
            sottocategorie = [c for c in canali_ascolto if c.startswith(canale + ".")]
            if sottocategorie:
                print(f"📺 Riceverai anche notifiche da: {', '.join(sottocategorie)}")
        else:
            print("❌ Canale non esistente o già iscritto.")
    
    elif scelta == "4":
        # Disiscriviti da canale
        canali_iscritto = db.ottieni_canali_utente(username)
        if canali_iscritto:
            print(f"\n📋 Canali a cui sei iscritto:")
            for canale in canali_iscritto:
                print(f"  • {canale}")
            canale = input("\nCanale da cui disiscriversi: ").strip()
            if db.disiscriviti_canale(username, canale):
                print(f"✅ Disiscritto da '{canale}'.")
            else:
                print("❌ Non sei iscritto a questo canale.")
        else:
            print("❌ Non sei iscritto a nessun canale.")
    
    elif scelta == "5":
        # Inizia ascolto (logica originale modificata per gerarchia)
        key_sottoscrizioni = f"sottoscrizioni:{username}"
        
        # Se non ha sottoscrizioni, chiede di inserirle
        if not r.exists(key_sottoscrizioni):
            print("\n❌ Nessun canale sottoscritto.")
            print("\n📺 Canali disponibili:")
            print(db.mostra_canali_gerarchici())
            canali_input = input("\nInserisci i canali separati da virgola: ").split(',')
            for c in canali_input:
                c = c.strip()
                if c in db.ottieni_canali_disponibili():
                    r.sadd(key_sottoscrizioni, c)
            print("✅ Canali sottoscritti salvati.")

        # Usa la funzione gerarchica per ottenere tutti i canali da ascoltare
        canali = db.ottieni_canali_ascolto(username)
        if not canali:
            print("❌ Nessun canale valido sottoscritto.")
            continue
            
        print(f"\n🎧 Ascolterò i canali: {canali}")

        # mostra ultime notifiche
        print("\n--- ULTIME NOTIFICHE ---")
        for c in canali:
            recenti = r.lrange(f"notifiche:{c}", -3, -1)
            if recenti:
                print(f"\n[{c}]:")
                for raw in recenti:
                    try:
                        dati = json.loads(raw)
                        print(f"  📩 {dati['titolo']} - {dati['messaggio']} (da {dati.get('autore', 'sconosciuto')})")
                    except:
                        pass

        pubsub = r.pubsub()
        pubsub.subscribe(*canali)

        stop_listening = threading.Event()
        
        def ascolta():
            try:
                for msg in pubsub.listen():
                    if stop_listening.is_set():
                        break
                    if msg['type'] == 'message':
                        try:
                            dati = json.loads(msg['data'])
                            canale = msg['channel']
                            print(f"\n🔔 [{canale}] {dati['titolo']}: {dati['messaggio']} (da {dati.get('autore', 'sconosciuto')})")
                        except:
                            pass
            except:
                pass  # Ignora errori di connessione chiusa

        listener_thread = threading.Thread(target=ascolta, daemon=True)
        listener_thread.start()

        try:
            print("📱 Ascolto notifiche... (Ctrl+C per tornare al menu)")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Tornato al menu.")
            stop_listening.set()
            pubsub.close()
    
    else:
        print("❌ Scelta non valida.")