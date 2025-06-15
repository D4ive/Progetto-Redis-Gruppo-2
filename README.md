# Sistema di Notifiche Redis 🔔

Un sistema di notifiche in tempo reale basato su Redis che permette di inviare e ricevere messaggi attraverso canali tematici gerarchici.

![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Caratteristiche

- 📡 **Notifiche Real-time**: Ricezione istantanea tramite Redis Pub/Sub
- 🏷️ **Canali Gerarchici**: Sistema smart di categorie (es. `sport.calcio.serieA`)
- 👥 **Multi-utente**: Gestione ruoli separati per produttori e consumatori
- 💾 **Persistenza**: Cronologia notifiche recenti con auto-pulizia
- 🔐 **Autenticazione**: Sistema login con profili utente persistenti
- ⚡ **Connessioni Multiple**: Supporto consumatori simultanei

## 🚀 Quick Start

### Prerequisiti
- Python 3.7+
- Redis Server
- Windows (per launcher automatico)

### Installazione

1. **Clona il repository**
   ```bash
   git clone https://github.com/D4ive/Progetto-Redis-Gruppo-2
   cd Progetto-Redis-Gruppo-2
   ```

2. **Installa dipendenze**
   ```bash
   pip install -r requirements.txt
   ```

3. **Avvia Redis Server**
   ```bash
   redis-server
   ```

4. **Lancia l'applicazione**
   ```bash
   python main.py
   ```

## 🎯 Come Usare

### 📤 Come Produttore
1. Scegli opzione `2` (Produttore)
2. Registrati o fai login
3. Crea canali tematici
4. Invia notifiche ai tuoi canali

```
--- MENU PRODUTTORE ---
1. Crea nuovo canale
2. Invia notifica

Esempio canale: sport.calcio.serieA
Titolo: Gol di Messi!
Messaggio: Incredibile gol al 90° minuto!
```

### 📥 Come Consumatore  
1. Scegli opzione `1` (Consumatore)
2. Registrati o fai login
3. Iscriviti ai canali di interesse
4. Inizia ad ascoltare le notifiche

```
--- MENU CONSUMATORE ---
1. Visualizza canali a cui sei iscritto
2. Visualizza canali disponibili  
3. Iscriviti a un canale
4. Disiscriviti da un canale
5. Inizia ad ascoltare notifiche

📩🔔 [sport.calcio] Gol di Messi!: Incredibile gol al 90° minuto! (da producer1, ora)
```

## 🌳 Sistema Canali Gerarchici

Il sistema supporta canali organizzati gerarchicamente:

```
📁 sport
  └── sport.calcio
      └── sport.calcio.serieA
  └── sport.tennis
📁 tecnologia  
  └── tecnologia.ai
      └── tecnologia.ai.chatgpt
📁 musica
📁 notizie
```

**Funzionalità Smart**: Iscrivendoti a `sport` ricevi automaticamente notifiche da `sport.calcio`, `sport.tennis`, ecc.

## 📁 Struttura Progetto

redis-notification-system/
├── redis_notification_system/
│   ├── __init__.py
│   ├── auth.py
│   ├── consumer.py
│   ├── database.py
│   └── producer.py
├── main.py
├── requirements.txt
├── README.md
└── .gitignore

## 🛠️ Esempi di Utilizzo

### Scenario 1: Notifiche Sportive
```bash
# Produttore crea canale
Nuovo canale: sport.calcio.champions

# Consumatore si iscrive a categoria generale  
Canale: sport

# Produttore invia notifica
[sport.calcio.champions] Risultato: Real Madrid 2-1 Barcelona

# Consumatore riceve automaticamente (iscritto a "sport")
📩🔔 [sport.calcio.champions] Risultato: Real Madrid 2-1 Barcelona (da sportNews, ora)
```

### Scenario 2: Multiple Sottoscrizioni
```bash
# Consumatore A: iscritto a ["tecnologia", "musica"]
# Consumatore B: iscritto a ["tecnologia.ai"]

# Notifica su "tecnologia.ai.openai"
# → Consumatore A: ✅ riceve (padre "tecnologia")
# → Consumatore B: ✅ riceve (padre "tecnologia.ai")
```

## 🔧 Funzionalità Tecniche

- **Persistenza**: Le ultime 10 notifiche per canale vengono conservate per 6 ore
- **Thread Safety**: Ascolto non-bloccante con gestione thread dedicati
- **Error Handling**: Gestione robusta di disconnessioni e errori Redis
- **Auto-cleanup**: Rimozione automatica notifiche obsolete
- **Feedback Stats**: Conta potenziali ricevitori per ogni notifica

## 🤝 Collaborazione

Questo progetto è stato sviluppato utilizzando Git per la collaborazione:
- Feature branches per nuove funzionalità
- Pull requests per code review
- Commit atomici e descrittivi
- Gestione conflitti e merge

## 📚 Documentazione

- **[Documentazione Tecnica](TECHNICAL_DOCS.md)** - Architettura, implementazione e scelte tecniche dettagliate
- **[Requirements](requirements.txt)** - Dipendenze Python necessarie

## 🐛 Troubleshooting

### Redis non si connette
```bash
# Verifica che Redis sia attivo
redis-cli ping
# Dovrebbe rispondere: PONG
```

### Errore di import
```bash
# Reinstalla dipendenze
pip install --upgrade redis
```

### Problemi Windows launcher
```bash
# Lancia direttamente i moduli
python producer.py  # Per produttore
python consumer.py  # Per consumatore
```

## 👨‍💻 Team (Austria, Di Ceglie, Lamanna, Morti)

**Gruppo 2** - Progetto Redis  
- Sviluppo collaborativo con Git
- Code review e pair programming
- Metodologia agile per iterazioni

## 📄 Licenza

Distribuito sotto licenza MIT. Vedi `LICENSE` per maggiori informazioni.

---

⭐ **Se questo progetto era fatto bene ci lasci un bel voto :D** ⭐