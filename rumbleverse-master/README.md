# Rumbleverse Master Server

Simple server browser backend for custom Rumbleverse servers.

## API

### Register

POST `/register`

```json
{
  "name": "My Rumbleverse Server",
  "ip": "1.2.3.4",
  "port": 62169,
  "players": 0,
  "max_players": 45,
  "game_mode": 1,
  "map": "Playground"
}
```

### Heartbeat

POST `/heartbeat`

```json
{
  "server_id": "SERVER_ID",
  "players": 5
}
```

### List servers

GET `/servers`

### Unregister

POST `/unregister`

```json
{
  "server_id": "SERVER_ID"
}
```