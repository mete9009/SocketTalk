import socket
import threading

clients = {}

def herkese_gonder(mesaj, haric=None):
    for isim, conn in clients.items():
        if isim != haric:
            try:
                conn.send(mesaj.encode())
            except:
                pass

def gruba_gonder(mesaj, grup, gonderen):
    for isim in grup:
        if isim in clients and isim != gonderen:
            try:
                clients[isim].send(mesaj.encode())
            except:
                pass

def handle_client(conn, addr):
    try:
        conn.send("AD:".encode())
        isim = conn.recv(1024).decode().strip()
        clients[isim] = conn
        print(f"{isim} bağlandı")
        herkese_gonder(f"LISTE:{','.join(clients.keys())}")
    except:
        conn.close()
        return

    while True:
        try:
            veri = conn.recv(1024).decode().strip()
            if not veri:
                break

            if veri.startswith("OZEL:"):
                _, hedef, mesaj = veri.split(":", 2)
                if hedef in clients:
                    clients[hedef].send(f"OZEL:{isim}:{mesaj}".encode())

            elif veri.startswith("BROADCAST:"):
                _, mesaj = veri.split(":", 1)
                herkese_gonder(f"BROADCAST:{isim}:{mesaj}", haric=isim)

            elif veri.startswith("GRUP:"):
                _, uyeler, mesaj = veri.split(":", 2)
                grup = uyeler.split(",")
                gruba_gonder(f"GRUP:{isim}:{mesaj}", grup, isim)

        except:
            break

    del clients[isim]
    herkese_gonder(f"LISTE:{','.join(clients.keys())}")
    conn.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 9999))
server.listen()
print("Sunucu basladi...")

while True:
    conn, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()