# Documentazione Tecnica - Sistema di Notifiche Redis

## Indice

1. [Panoramica del Progetto](https://claude.ai/chat/950bc282-a3df-4450-8926-0d78aaa0d1d6#panoramica-del-progetto)
2. [Architettura del Sistema](https://claude.ai/chat/950bc282-a3df-4450-8926-0d78aaa0d1d6#architettura-del-sistema)
3. [Strutture Dati](https://claude.ai/chat/950bc282-a3df-4450-8926-0d78aaa0d1d6#strutture-dati)
4. [Implementazione dei Componenti](https://claude.ai/chat/950bc282-a3df-4450-8926-0d78aaa0d1d6#implementazione-dei-componenti)
5. [Scelte Tecniche](https://claude.ai/chat/950bc282-a3df-4450-8926-0d78aaa0d1d6#scelte-tecniche)
6. [Gestione degli Errori](https://claude.ai/chat/950bc282-a3df-4450-8926-0d78aaa0d1d6#gestione-degli-errori)
7. [Guida all'Utilizzo](https://claude.ai/chat/950bc282-a3df-4450-8926-0d78aaa0d1d6#guida-allutilizzo)
8. [Limitazioni e Miglioramenti Futuri](https://claude.ai/chat/950bc282-a3df-4450-8926-0d78aaa0d1d6#limitazioni-e-miglioramenti-futuri)

## Panoramica del Progetto

Il **Sistema di Notifiche Redis** è un'applicazione distribuita in tempo reale che permette di inviare e ricevere notifiche attraverso canali tematici. Il sistema implementa un pattern Publisher-Subscriber utilizzando Redis come broker di messaggi e sistema di persistenza.

### Obiettivi Raggiunti

- ✅ Notifiche in tempo reale con titolo e messaggio
- ✅ Sistema di canali gerarchici (es. sport.calcio.serieA)
- ✅ Persistenza delle notifiche recenti con auto-eliminazione
- ✅ Supporto multi-utente con autenticazione
- ✅ Profili utente persistenti con preferenze canali
- ✅ Supporto connessioni multiple simultanee

## Architettura del Sistema

### Diagramma Architetturale

```
┌─────────────────┐    ┌─────────────────┐    ┌──────────────────┐
│   Producer(s)   │    │      Redis      │    │   Consumer(s)    │
│                 │    │                 │    │                  │
│ • Autenticazione│◄──►│ • Pub/Sub       │◄──►│ • Autenticazione │
│ • Creazione     │    │ • Database      │    │ • Sottoscrizioni │
│   Canali        │    │ • Persistenza   │    │ • Ascolto Real-  │
│ • Invio         │    │ • Gestione      │    │   time           │
│   Notifiche     │    │   Utenti        │    │                  │
└─────────────────┘    └─────────────────┘    └──────────────────┘
```

### Pattern Architetturali Utilizzati

1. **Publisher-Subscriber Pattern**: Core del sistema per la distribuzione delle notifiche
2. **Repository Pattern**: Astrazione dell'accesso ai dati Redis tramite `database.py`
3. **Separation of Concerns**: Moduli separati per autenticazione, database e logica applicativa
4. **Command Pattern**: Menu interattivi con gestione comandi discreti

## Strutture Dati

### Strutture Redis Utilizzate

#### 1. SET - Gestione Utenti

```redis
# Utenti registrati per ruolo
utenti:produttore:registrati → SET {username1, username2, ...}
utenti:consumatore:registrati → SET {username1, username2, ...}
```

#### 2. HASH - Dati Utente

```redis
# Dati specifici utente
utenti:{ruolo}:{username} → HASH {
    "email": "user@example.com",
    "password": "hashedpassword"
}
```

#### 3. SET - Canali e Sottoscrizioni

```redis
# Canali disponibili
elenco_canali → SET {sport, sport.calcio, musica, notizie, ...}

# Sottoscrizioni utente
sottoscrizioni:{username} → SET {sport, musica, ...}
```

#### 4. LIST - Persistenza Notifiche

```redis
# Notifiche recenti per canale (FIFO con limite)
notifiche:{canale} → LIST [notifica_recente, ..., notifica_meno_recente]
```

#### 5. PUB/SUB - Distribuzione Real-time

```python
# Canali di pubblicazione
PUBLISH sport.calcio '{"titolo": "Gol!", "messaggio": "...", ...}'
```

### Struttura Dati Notifica

```json
{
    "titolo": "string",
    "messaggio": "string", 
    "timestamp": float,
    "autore": "string"
}
```

## Implementazione dei Componenti

### 1. Core Module (`database.py`)

#### Connessione Redis

```python
def connection():
    redis_client = redis.Redis(decode_responses=True, host='localhost', port=6379, db=0)
    if not redis_client.ping():
        raise Exception("Redis non funzionante")
    return redis_client
```

**Scelta Tecnica**: `decode_responses=True` per gestire automaticamente la codifica UTF-8, semplificando il handling delle stringhe.

#### Gestione Canali Gerarchici

La funzione `ottieni_canali_ascolto()` implementa la logica gerarchica:

```python
def ottieni_canali_ascolto(username):
    canali_iscritto = list(r.smembers(key_sottoscrizioni))
    
    for canale_iscritto in canali_iscritto:
        canali_da_ascoltare.add(canale_iscritto)
        
        # Logica gerarchica: sport include sport.calcio, sport.tennis, etc.
        for canale_esistente in tutti_canali:
            if canale_esistente.startswith(canale_iscritto + "."):
                canali_da_ascoltare.add(canale_esistente)
```

**Vantaggio**: Un utente iscritto a "sport" riceve automaticamente notifiche da "sport.calcio", "sport.tennis", etc.

#### Persistenza con Auto-pulizia

```python
def crea_notifica(canale, notifica):
    # Real-time
    r.publish(canale, json.dumps(notifica))
    
    # Persistenza
    r.lpush(f"notifiche:{canale}", json.dumps(notifica))
    r.ltrim(f"notifiche:{canale}", 0, 9)  # Mantieni solo 10 più recenti
    r.expire(f"notifiche:{canale}", 3600 * 6)  # TTL di 6 ore
```

**Scelta Tecnica**: Uso di `LPUSH` + `LTRIM` per mantenere un buffer circolare efficiente delle notifiche recenti.

### 2. Authentication Module (`auth.py`)

#### Sistema di Tentativi Limitati

```python
def login_utente():
    max_tentativi = 3
    
    # Doppia validazione: username poi password
    for tentativo in range(max_tentativi):
        # Logica tentativo con feedback progressivo
```

**Scelta di Sicurezza**: Limite tentativi per prevenire attacchi brute-force, con feedback informativo all'utente.

#### Separazione Ruoli

```python
def ottieni_ruolo_utente(username):
    if r.sismember("utenti:produttore:registrati", username):
        return "produttore"
    elif r.sismember("utenti:consumatore:registrati", username):
        return "consumatore"
```

**Vantaggio**: Controllo accessi basato su ruoli, un utente può essere solo produttore O consumatore.

### 3. Producer Application (`producer.py`)

#### Creazione Dinamica Canali

```python
if nuovo_canale not in db.ottieni_canali_disponibili():
    db.aggiungi_canali([nuovo_canale])
```

**Flessibilità**: I produttori possono creare nuovi canali dinamicamente, supportando l'espansione organica del sistema.

#### Feedback Statistiche

```python
print(f"📊 Potenziali ricevitori: {db.conta_potenziali_ricevitori(canale)}")
```

**UX Enhancement**: Il produttore vede immediatamente quanti utenti riceveranno la notifica.

### 4. Consumer Application (`consumer.py`)

#### Threading per Ascolto Non-bloccante

```python
def ascolta():
    for msg in pubsub.listen():
        if stop_listening.is_set():
            break
        # Gestione messaggio

listener_thread = threading.Thread(target=ascolta, daemon=True)
```

**Scelta Tecnica**: Thread daemon per ascolto in background, permettendo interruzione pulita via KeyboardInterrupt.

#### Gestione Timestamp Intelligente

```python
def calcola_tempo_trascorso(timestamp):
    secondi_passati = time.time() - float(timestamp)
    ore = int(secondi_passati // 3600)
    minuti = int((secondi_passati % 3600) // 60)
    
    if ore > 0:
        return f"{ore}h fa"
    elif minuti > 0:
        return f"{minuti}m fa"
    else:
        return "ora"
```

**UX**: Mostra tempo relativo sia per notifiche storiche che real-time.

## Scelte Tecniche

### 1. Redis come Backend

**Vantaggi**:

- Pub/Sub nativo per real-time messaging
- Strutture dati ricche (SET, LIST, HASH)
- Persistenza configurabile
- Performance elevate
- TTL automatico per pulizia dati

**Alternative Considerate**: Apache Kafka (troppo complesso), RabbitMQ (meno strutture dati)

### 2. Python con Redis-py

**Vantaggi**:

- Binding ufficiale Redis
- Supporto completo PubSub
- Gestione automatica connessioni
- Decode automatico UTF-8

### 3. Architettura Modulare

```
auth.py      → Autenticazione e gestione ruoli
database.py  → Astrazione accesso dati Redis  
producer.py  → Logica creazione/invio notifiche
consumer.py  → Logica ricezione/display notifiche
```

**Vantaggio**: Separazione responsabilità, manutenibilità, testabilità.

### 4. CLI Interattiva

**Scelta UX**: Menu testuali per semplicità deployment e debug, evitando dipendenze GUI.

## Gestione degli Errori

### 1. Connettività Redis

```python
def connection():
    if not redis_client.ping():
        raise Exception("Redis non funzionante")
```

### 2. Parsing JSON Sicuro

```python
try:
    dati = json.loads(msg['data'])
except json.JSONDecodeError:
    pass  # Ignora messaggi malformati
```

### 3. Gestione Interruzioni

```python
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n👋 Tornato al menu.")
    stop_listening.set()
    pubsub.close()
```

### 4. Validazione Input Utente

```python
while (inp.strip() not in ["1", "2"]):
    inp = input("Scelta non valida. Digita 1 o 2: ").strip()
```

## Guida all'Utilizzo

### Prerequisiti

1. **Redis Server** attivo su localhost:6379
2. **Python 3.7+** con libreria `redis`
3. **Sistema Operativo**: Windows (per `subprocess` launch)

### Installazione

```bash
git clone https://github.com/D4ive/Progetto-Redis-Gruppo-2
cd Progetto-Redis-Gruppo-2
pip install -r requirements.txt
```

### Avvio Sistema

```bash
python main.py
```

### Workflow Tipico

#### Setup Iniziale

1. **Avvia Redis**: `redis-server`
2. **Lancia main.py**
3. **Scegli ruolo**: Produttore (2) o Consumatore (1)

#### Come Produttore

1. **Registrati/Login** con ruolo "produttore"
2. **Crea Canali**: es. "sport", "sport.calcio", "tecnologia.ai"
3. **Invia Notifiche**: seleziona canale, inserisci titolo/messaggio
4. **Visualizza Statistiche**: vedi quanti utenti riceveranno la notifica

#### Come Consumatore

1. **Registrati/Login** con ruolo "consumatore"
2. **Gestisci Sottoscrizioni**:
    - Visualizza canali disponibili
    - Iscriviti a canali di interesse
    - Visualizza sottoscrizioni attuali
3. **Avvia Ascolto**: ricevi notifiche real-time
4. **Visualizza Cronologia**: vedi ultime notifiche anche offline

### Esempi di Utilizzo

#### Scenario: Notifiche Sportive

```
Produttore:
1. Crea canale "sport.calcio.serieA"
2. Invia notifica: "Gol di Ronaldo al 45°!"

Consumatore iscritto a "sport":
- Riceve automaticamente notifica da "sport.calcio.serieA"
- Vede: "📩🔔 [sport.calcio.serieA] Gol di Ronaldo al 45°! (da producer1, ora)"
```

#### Scenario: Multi-Consumatore

```
Consumer A: iscritto a ["sport", "tecnologia"]
Consumer B: iscritto a ["sport.tennis"] 
Consumer C: iscritto a ["tecnologia.ai"]

Notifica su "tecnologia.ai.chatgpt":
- Consumer A: ✅ riceve (iscritto a "tecnologia")  
- Consumer B: ❌ non riceve
- Consumer C: ✅ riceve (iscritto a "tecnologia.ai")
```


```

---

**Progetto sviluppato dal Gruppo 2**  
**Repository**: https://github.com/D4ive/Progetto-Redis-Gruppo-2  
**Tecnologie**: Python, Redis, redis-py  
**Pattern**: Publisher-Subscriber, Repository, Command