import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox

# ---- Ağ ----
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 9999))

# ---- Global değişkenler ----
kullanici_adi = ""
aktif_hedef = None
aktif_mod = "ozel"  # ozel, broadcast, grup
secili_grup = []

# ---- Mesaj al ----
def mesaj_al():
    while True:
        try:
            veri = client.recv(1024).decode().strip()

            if veri.startswith("AD:"):
                client.send(kullanici_adi.encode())

            elif veri.startswith("LISTE:"):
                kisiler = veri.split(":")[1].split(",")
                kisiler = [k for k in kisiler if k and k != kullanici_adi]
                kisi_listesi.delete(0, tk.END)
                for k in kisiler:
                    kisi_listesi.insert(tk.END, k)

            elif veri.startswith("OZEL:"):
                _, gonderen, mesaj = veri.split(":", 2)
                mesaj_ekle(f"[Özel] {gonderen}: {mesaj}")

            elif veri.startswith("BROADCAST:"):
                _, gonderen, mesaj = veri.split(":", 2)
                mesaj_ekle(f"[Herkese] {gonderen}: {mesaj}")

            elif veri.startswith("GRUP:"):
                _, gonderen, mesaj = veri.split(":", 2)
                mesaj_ekle(f"[Grup] {gonderen}: {mesaj}")

        except:
            break

def mesaj_ekle(mesaj):
    sohbet.config(state=tk.NORMAL)
    sohbet.insert(tk.END, mesaj + "\n")
    sohbet.config(state=tk.DISABLED)
    sohbet.see(tk.END)

# ---- Mesaj gönder ----
def mesaj_gonder(event=None):
    mesaj = giris.get().strip()
    if not mesaj:
        return

    if aktif_mod == "ozel":
        if not aktif_hedef:
            messagebox.showwarning("Uyarı", "Bir kişi seç!")
            return
        client.send(f"OZEL:{aktif_hedef}:{mesaj}".encode())
        mesaj_ekle(f"[Özel] Sen → {aktif_hedef}: {mesaj}")

    elif aktif_mod == "broadcast":
        client.send(f"BROADCAST:{mesaj}".encode())
        mesaj_ekle(f"[Herkese] Sen: {mesaj}")

    elif aktif_mod == "grup":
        if not secili_grup:
            messagebox.showwarning("Uyarı", "Grup üyesi seç!")
            return
        uyeler = ",".join(secili_grup)
        client.send(f"GRUP:{uyeler}:{mesaj}".encode())
        mesaj_ekle(f"[Grup] Sen: {mesaj}")

    giris.delete(0, tk.END)

# ---- Kişi seç ----
def kisi_sec(event):
    global aktif_hedef, aktif_mod
    secim = kisi_listesi.curselection()
    if secim:
        aktif_hedef = kisi_listesi.get(secim[0])
        aktif_mod = "ozel"
        mod_label.config(text=f"Mod: Özel → {aktif_hedef}")

# ---- Arama ----
def ara(event=None):
    aranan = arama_giris.get().lower()
    kisi_listesi.delete(0, tk.END)
    for k in tum_kisiler:
        if aranan in k.lower():
            kisi_listesi.insert(tk.END, k)

tum_kisiler = []

# ---- Mod seç ----
def broadcast_mod():
    global aktif_mod
    aktif_mod = "broadcast"
    mod_label.config(text="Mod: Herkese Broadcast")

def grup_mod():
    global aktif_mod, secili_grup
    aktif_mod = "grup"
    secimler = kisi_listesi.curselection()
    secili_grup = [kisi_listesi.get(i) for i in secimler]
    mod_label.config(text=f"Mod: Grup → {', '.join(secili_grup)}")

# ---- Arayüz ----
pencere = tk.Tk()
pencere.withdraw()

kullanici_adi = simpledialog.askstring("SocketTalk", "Kullanıcı adınız:")
pencere.title(f"SocketTalk - {kullanici_adi}")
pencere.deiconify()
pencere.geometry("700x500")

# Sol panel - kişiler
sol = tk.Frame(pencere, width=200, bg="#2b2b2b")
sol.pack(side=tk.LEFT, fill=tk.Y)

tk.Label(sol, text="Kişiler", bg="#2b2b2b", fg="white", font=("Arial", 12, "bold")).pack(pady=5)

arama_giris = tk.Entry(sol, width=22)
arama_giris.pack(padx=5, pady=3)
arama_giris.bind("<KeyRelease>", ara)
arama_giris.insert(0, "Ara...")

kisi_listesi = tk.Listbox(sol, width=25, height=20, selectmode=tk.MULTIPLE, bg="#3c3f41", fg="white")
kisi_listesi.pack(padx=5, pady=5)
kisi_listesi.bind("<<ListboxSelect>>", kisi_sec)

tk.Button(sol, text="Gruba Ekle", command=grup_mod, bg="#4a90d9", fg="white", width=20).pack(pady=2)
tk.Button(sol, text="Herkese Gönder", command=broadcast_mod, bg="#e74c3c", fg="white", width=20).pack(pady=2)

# Sağ panel - sohbet
sag = tk.Frame(pencere)
sag.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

mod_label = tk.Label(sag, text="Mod: Kişi seç", bg="#1e1e1e", fg="white")
mod_label.pack(fill=tk.X)

sohbet = tk.Text(sag, state=tk.DISABLED, bg="#1e1e1e", fg="white", font=("Arial", 11))
sohbet.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

alt = tk.Frame(sag)
alt.pack(fill=tk.X, padx=5, pady=5)

giris = tk.Entry(alt, font=("Arial", 11))
giris.pack(side=tk.LEFT, fill=tk.X, expand=True)
giris.bind("<Return>", mesaj_gonder)

tk.Button(alt, text="Gönder", command=mesaj_gonder, bg="#4a90d9", fg="white").pack(side=tk.LEFT, padx=5)

# ---- Başlat ----
thread = threading.Thread(target=mesaj_al)
thread.daemon = True
thread.start()

pencere.mainloop()