import redis

def connection():
    redis_client = redis.Redis(decode_responses=True, host='localhost', port=6379, db=0)
    if not redis_client.ping():
        raise Exception("Redis non funzionante")
    return redis_client

def aggiungi_canali(canali = ['sport', 'musica', 'notizie', 'intrattenimento']):
    r = connection()
    r.sadd('elenco_canali', *canali)