# Redis Notification System

## Overview
The Redis Notification System is a simple application that allows for real-time notifications using Redis as the messaging broker. The system consists of two main components: a Producer that creates and sends notifications, and a Consumer that listens for and displays those notifications.

## Features
- **Producer**: Sends notifications to specified Redis channels.
- **Consumer**: Subscribes to channels and displays notifications in real-time.

## Project Structure
```
redis-notification-system
├── producer
│   ├── producer.py       # Logic for sending notifications
│   └── __init__.py       # Package initialization for producer
├── consumer
│   ├── consumer.py       # Logic for receiving notifications
│   └── __init__.py       # Package initialization for consumer
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
```

## Setup Instructions
1. Clone the repository:
   ```
   git clone <repository-url>
   cd redis-notification-system
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Ensure you have a running Redis server. You can start a Redis server locally using Docker:
   ```
   docker run -p 6379:6379 -d redis
   ```

## Usage
### Producer
To send a notification, run the `producer.py` script:
```
python producer/producer.py
```
You can modify the script to send different notifications by changing the parameters in the `send_notification` method.

### Consumer
To receive notifications, run the `consumer.py` script:
```
python consumer/consumer.py
```
The consumer will listen for notifications on the specified channel and display them in real-time.

## Dependencies
- `redis`: Python client for Redis.

## License
This project is licensed under the MIT License.