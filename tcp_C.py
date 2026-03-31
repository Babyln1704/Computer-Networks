import socket
import ssl
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os

SERVER_IP = "10.20.203.56"
PORT = 5000
BUFFER = 65536

selected_files = []


def log(msg):
    text_box.insert(tk.END, msg + "\n")
    text_box.see(tk.END)


def choose_file():
    global selected_files
    selected_files = filedialog.askopenfilenames()

    for f in selected_files:
        log("Selected: " + f)


def upload_file():
    if not selected_files:
        messagebox.showerror("Error", "Select files first")
        return

    for f in selected_files:
        threading.Thread(target=upload_process, args=(f,)).start()


def upload_process(file_path):
    try:
        fmt = format_var.get()

        context = ssl._create_unverified_context()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client = context.wrap_socket(sock, server_hostname="localhost")

        client.connect((SERVER_IP, PORT))

        filename = os.path.basename(file_path)

        client.send((filename + "|" + fmt).encode())

        with open(file_path, "rb") as f:
            data = f.read()

        client.send(str(len(data)).encode().ljust(16))
        client.sendall(data)

        log(f"Uploading {filename}...")

        response = client.recv(1024)

        if response == b"ERROR":
            log(f"{filename} ❌ Unsupported format")
            return

        server_filename = response.decode().strip()

        size_data = client.recv(16).decode().strip()
        if not size_data:
            log("Error receiving file")
            return

        size = int(size_data)

        received = b''
        while len(received) < size:
            received += client.recv(BUFFER)

        with open(server_filename, "wb") as f:
            f.write(received)

        log(f"{filename} ✅ Done")

        client.close()

    except Exception as e:
        messagebox.showerror("Error", str(e))


# GUI
root = tk.Tk()
root.title("Secure File Converter")
root.geometry("520x500")
root.configure(bg="#1e1e2f")

tk.Label(root, text="Secure File Converter",
         font=("Arial", 16, "bold"),
         bg="#1e1e2f", fg="#00ffcc").pack(pady=10)

tk.Button(root, text="Select Files",
          bg="#4CAF50", fg="white",
          command=choose_file).pack(pady=10)

format_var = tk.StringVar()
format_menu = ttk.Combobox(root, textvariable=format_var, width=20)
format_menu["values"] = ("pdf", "docx", "txt", "jpg", "png", "csv")
format_menu.current(0)
format_menu.pack(pady=10)

tk.Button(root, text="Upload & Convert",
          bg="#2196F3", fg="white",
          command=upload_file).pack(pady=10)

text_box = tk.Text(root, height=18, width=60,
                   bg="#0f172a", fg="#22c55e")
text_box.pack(pady=10)

root.mainloop()