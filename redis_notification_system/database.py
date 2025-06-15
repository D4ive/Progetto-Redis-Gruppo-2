import redis
import json

def connection():
    """Stabilisce connessione Redis"""
    redis_client = redis.Redis(decode_responses=True, host='localhost', port=6379, db=0)
    if not redis_client.ping():
        raise Exception("Redis non funzionante")
    return redis_client

# === GESTIONE UTENTI ===

def utente_esiste(username, ruolo):
    """Verifica se un utente esiste già per un dato ruolo"""
    r = connection()
    key_set = f"utenti:{ruolo}:registrati"
    return r.sismember(key_set, username)

def crea_utente(username, ruolo, email, password):
    """Crea un nuovo utente nel database"""
    try:
        r = connection()
        key_set = f"utenti:{ruolo}:registrati"
        key_hash = f"utenti:{ruolo}:{username}"
        
        r.sadd(key_set, username)
        r.hset(key_hash, mapping={
            "email": email,
            "password": password
        })
        return True
    except Exception:
        return False

def ottieni_ruolo_utente(username):
    """Trova il ruolo di un utente registrato"""
    r = connection()
    
    if r.sismember("utenti:produttore:registrati", username):
        return "produttore"
    elif r.sismember("utenti:consumatore:registrati", username):
        return "consumatore"
    else:
        return None

def verifica_password(username, ruolo, password):
    """Verifica la password di un utente"""
    r = connection()
    key_hash = f"utenti:{ruolo}:{username}"
    saved_password = r.hget(key_hash, "password")
    return saved_password is not None and saved_password == password

# === GESTIONE CANALI ===

def aggiungi_canali(canali=['sport', 'musica', 'notizie', 'intrattenimento']):
    """Aggiunge canali all'elenco disponibile"""
    r = connection()
    r.sadd('elenco_canali', *canali)

def ottieni_canali_disponibili():
    """Restituisce tutti i canali disponibili"""
    r = connection()
    canali = list(r.smembers('elenco_canali'))
    return sorted(canali) if canali else []

def mostra_canali_gerarchici():
    """Mostra i canali in formato gerarchico"""
    canali = ottieni_canali_disponibili()
    if not canali:
        return "Nessun canale disponibile."
    
    # Organizza canali per gerarchia
    gerarchici = {}
    for canale in canali:
        parti = canale.split('.')
        if len(parti) == 1:
            # Canale principale
            if canale not in gerarchici:
                gerarchici[canale] = []
        else:
            # Sottocategoria
            principale = parti[0]
            if principale not in gerarchici:
                gerarchici[principale] = []
            gerarchici[principale].append(canale)
    
    # Formatta output
    output = []
    for principale in sorted(gerarchici.keys()):
        output.append(f"📁 {principale}")
        sottocategorie = sorted(gerarchici[principale])
        for sotto in sottocategorie:
            output.append(f"  └── {sotto}")
    
    return "\n".join(output)

# === GESTIONE ISCRIZIONI ===

def ottieni_canali_utente(username):
    """Restituisce i canali a cui un utente è iscritto"""
    r = connection()
    key_sottoscrizioni = f"sottoscrizioni:{username}"
    if r.exists(key_sottoscrizioni):
        print("Entra qui")
        canali = list(r.smembers(key_sottoscrizioni))
        return sorted(canali) if canali else []
    else:
        print("Entra quo")
        return False

def ottieni_canali_ascolto(username):
    """Restituisce tutti i canali che l'utente deve ascoltare (incluse sottocategorie)"""
    r = connection()
    key_sottoscrizioni = f"sottoscrizioni:{username}"
    canali_iscritto = list(r.smembers(key_sottoscrizioni))
    tutti_canali = list(r.smembers('elenco_canali'))
    
    canali_da_ascoltare = set()
    
    for canale_iscritto in canali_iscritto:
        # Aggiungi il canale principale
        canali_da_ascoltare.add(canale_iscritto)
        
        # Aggiungi tutte le sottocategorie
        for canale_esistente in tutti_canali:
            if canale_esistente.startswith(canale_iscritto + "."):
                canali_da_ascoltare.add(canale_esistente)
    
    return sorted(list(canali_da_ascoltare))

def iscriviti_canale(username, canale):
    """Iscrive un utente a un canale"""
    r = connection()
    key_sottoscrizioni = f"sottoscrizioni:{username}"
    
    if not r.sismember('elenco_canali', canale):
        return False
    if r.sismember(key_sottoscrizioni, canale):
        return False
    
    r.sadd(key_sottoscrizioni, canale)
    return True

def disiscriviti_canale(username, canale):
    """Disiscrive un utente da un canale"""
    r = connection()
    key_sottoscrizioni = f"sottoscrizioni:{username}"
    
    if not r.sismember(key_sottoscrizioni, canale):
        return False
    
    r.srem(key_sottoscrizioni, canale)
    return True

# === GESTIONE NOTIFICHE ===

def crea_notifica(canale, notifica):
    """Crea e pubblica una notifica su un canale"""
    r = connection()
    aggiungi_canali([canale])
    r.publish(canale, json.dumps(notifica))

    r.hset(name=f"notifiche:{canale}", 
           mapping={"titolo": notifica["titolo"],
                    "messaggio": notifica["messaggio"],
                    "timestamp": notifica["timestamp"],
                    "autore": notifica["autore"]
                    }
    )
    
    r.expire(f"notifiche:{canale}", 3600 * 6)
    return True

def conta_potenziali_ricevitori(canale):
    """Conta quanti utenti potrebbero ricevere una notifica per un dato canale"""
    r = connection()
    tutti_utenti = r.keys("sottoscrizioni:*")
    ricevitori = 0
    
    for utente_key in tutti_utenti:
        username_utente = utente_key.split(":")[1]
        canali_ascolto = ottieni_canali_ascolto(username_utente)
        if canale in canali_ascolto:
            ricevitori += 1
    
    return ricevitori