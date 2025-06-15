import redis
import json

def connection():
    redis_client = redis.Redis(decode_responses=True, host='localhost', port=6379, db=0)
    if not redis_client.ping():
        raise Exception("Redis non funzionante")
    return redis_client

def aggiungi_canali(canali = ['sport', 'musica', 'notizie', 'intrattenimento']):
    r = connection()
    r.sadd('elenco_canali', *canali)

def crea_notifica(canale, notifica):
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

# Funzioni aggiunte per gestire canali e iscrizioni
def ottieni_canali_disponibili():
    r = connection()
    canali = list(r.smembers('elenco_canali'))
    return sorted(canali) if canali else []

def ottieni_canali_utente(username):
    r = connection()
    key_sottoscrizioni = f"sottoscrizioni:{username}"
    canali = list(r.smembers(key_sottoscrizioni))
    return sorted(canali) if canali else []

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
    r = connection()
    key_sottoscrizioni = f"sottoscrizioni:{username}"
    
    if not r.sismember('elenco_canali', canale):
        return False
    if r.sismember(key_sottoscrizioni, canale):
        return False
    
    r.sadd(key_sottoscrizioni, canale)
    return True

def disiscriviti_canale(username, canale):
    r = connection()
    key_sottoscrizioni = f"sottoscrizioni:{username}"
    
    if not r.sismember(key_sottoscrizioni, canale):
        return False
    
    r.srem(key_sottoscrizioni, canale)
    return True

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