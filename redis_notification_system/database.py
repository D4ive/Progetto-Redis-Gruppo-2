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