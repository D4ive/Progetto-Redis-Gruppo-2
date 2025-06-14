import database as db

r = db.connection()

def registra_utente(ruolo):
    key_set = f"utenti:{ruolo}:registrati"
    username = input("Scegli uno username: ").strip()
    key_hash = f"utenti:{ruolo}:{username}"
    if r.sismember(key_set, username):
        print(f"L'utente '{username}' è già registrato come {ruolo}.")
        return None
    email = input("Inserisci la tua email: ")
    password = input("Scegli una password: ")
    r.sadd(key_set, username)
    r.hset(key_hash, mapping={
        "email": email,
        "password": password
    })
    print(f"Utente '{username}' registrato con successo come {ruolo}.")
    return username, ruolo

def menu_principale(ruolo):
    while True:
        try:
            print(f"--- {ruolo.upper()} DI NOTIFICHE ---")
            print("1. Registrati")
            print("2. Login")
            scelta = input("Scegli un'opzione: ").strip()
            
            if scelta == "1":
                result = registra_utente(ruolo)
                if result:
                    return result
                else:
                    continue  # Se registrazione fallisce, torna al menu
            elif scelta == "2":
                result = login_utente()
                if result[0]:  # Se login ha successo
                    return result
                else:
                    continue  # Se login fallisce, torna al menu
            else:
                print("Scelta non valida. Riprova.")
                continue
        except KeyboardInterrupt:
            print("\nUscita dal programma.")
            return None, None
        except Exception as e:
            print(f"Errore: {e}")
            continue

def login_utente():
    max_tentativi = 3
    
    # Gestione tentativi per username
    for tentativo in range(max_tentativi):
        username = input("Username: ").strip()
        ruolo = None
        
        if r.sismember("utenti:produttore:registrati", username):
            ruolo = "produttore"
            break
        elif r.sismember("utenti:consumatore:registrati", username):
            ruolo = "consumatore"
            break
        else:
            tentativi_rimasti = max_tentativi - tentativo - 1
            if tentativi_rimasti > 0:
                print(f"Utente non registrato. Ti rimangono {tentativi_rimasti} tentativi.")
            else:
                print("Troppi tentativi falliti per l'username. Accesso negato.")
                return None, None
    
    # Gestione tentativi per password
    key_hash = f"utenti:{ruolo}:{username}"
    for tentativo in range(max_tentativi):
        password = input("Inserisci la password: ").strip()
        saved_password = r.hget(key_hash, "password")
        
        if saved_password is not None and saved_password == password:
            print(f"Login effettuato. Benvenuto {username} ({ruolo})!")
            return username, ruolo
        else:
            tentativi_rimasti = max_tentativi - tentativo - 1
            if tentativi_rimasti > 0:
                print(f"Password errata. Ti rimangono {tentativi_rimasti} tentativi.")
            else:
                print("Troppi tentativi falliti per la password. Accesso negato.")
                return None, None