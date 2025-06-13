import __init__
import database as db

r = db.connection()

def chiedi_ruolo():
    while True:
        scelta = input("Sei un produttore o un consumatore? [1/2]: ").strip().lower()
        if scelta == "1":
            ruolo = "produttore"
        elif scelta == "2":
            ruolo = "consumatore"
        else:
            print("Scelta non valida. Riprova.")
            continue
        return ruolo

def mostra_utenti_registrati():
    utenti = r.smembers("utenti:registrati")
    if utenti:
        print("Utenti registrati disponibili:")
        for u in utenti:
            print(f" - {u}")
    else:
        print("Nessun utente registrato al momento.")



def registra_utente():
    ruolo = chiedi_ruolo()
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

def login_utente():
    username = input("Username: ").strip()
    ruolo = None
    if r.sismember("utenti:produttore:registrati", username):
        ruolo = "produttore"
    elif r.sismember("utenti:consumatore:registrati", username):
        ruolo = "consumatore"
    else:
        print("Utente non registrato.")
        return None, None
    key_hash = f"utenti:{ruolo}:{username}"
    password = input("Inserisci la password: ").strip()
    saved_password = r.hget(key_hash, "password")
    if saved_password is None or saved_password != password:
        print("Password errata.")
        return None, None
    print(f"Login effettuato. Benvenuto {username} ({ruolo})!")
    return username, ruolo

if __name__ == "__main__":
    print("1. Registrati\n2. Login")
    scelta = input("Scegli un'opzione: ")
    if scelta == "1":
        registra_utente()
    elif scelta == "2":
        login_utente()
    else:
        print("Opzione non valida.")