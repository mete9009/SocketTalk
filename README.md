# SocketTalk

A real-time chat application built with TCP sockets from scratch.

## Features
- One-to-one private messaging
- Broadcast to everyone
- Group messaging
- User search

## Requirements
- Python 3.x
- No extra libraries needed

## Usage

### Server (run once on host machine)
python server.py

### Client (run on each machine)
python client.py

## Important
In client.py, find this line:
client.connect(("127.0.0.1", 9999))

- If you are on the same machine as the server, leave it as 127.0.0.1
- If you are on a different machine, replace 127.0.0.1 with the server's local IP address (e.g. 192.168.1.5)
- To find the server's IP: run ipconfig on Windows or ip a on Linux

## Notes
- All devices must be on the same network (LAN)
- Server must be running before clients connect
