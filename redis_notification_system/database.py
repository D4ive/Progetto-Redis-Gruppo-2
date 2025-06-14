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