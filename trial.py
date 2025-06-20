import cv2
import os
import time
import numpy as np
import face_recognition
import urllib.request
import requests
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk

ESP32_CAM_URL = "http://<your-esp32-ip>/cam-hi.jpg"
BOT_TOKEN = "<your-telegram-bot-token>"
CHAT_ID = "<your-chat-id>"
FACE_MATCH_THRESHOLD = 0.45  

script_dir = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(script_dir, 'image_folder')
INTRUDER_FOLDER = os.path.join(script_dir, 'intruder_images')


os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs(INTRUDER_FOLDER, exist_ok=True)



def load_images():
    images, names = [], []
    for file in os.listdir(IMAGE_FOLDER):
        if file.lower().endswith(('.jpg', '.png')):
            img = cv2.imread(os.path.join(IMAGE_FOLDER, file))
            images.append(img)
            name = ''.join(filter(str.isalpha, os.path.splitext(file)[0])).capitalize()
            names.append(name)
    return images, names


def encode_faces(images):
    encodings = []
    for img in images:
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb)
        enc = face_recognition.face_encodings(rgb, boxes)
        if enc:
            encodings.append(enc[0])
    return encodings


def send_telegram_alert(image_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(image_path, 'rb') as photo:
        data = {"chat_id": CHAT_ID}
        files = {"photo": photo}
        requests.post(url, data=data, files=files)


class FaceSurveillanceApp:
    def __init__(self, master):
        self.master = master
        master.title("Smart Surveillance System")
        master.geometry("950x700")
        master.configure(bg="#1e1e2e")

        self.known_images, self.known_names = load_images()
        self.known_encodings = encode_faces(self.known_images)
        self.running = False

        self.setup_gui()

    def setup_gui(self):
        tk.Label(self.master, text="Smart Surveillance System",
                 font=("Helvetica", 20, "bold"), bg="#1e1e2e", fg="#f8f8f2").pack(pady=10)

        self.main_frame = tk.Frame(self.master, bg="#1e1e2e")
        self.video_frame = tk.Frame(self.main_frame, bg="#1e1e2e")
        self.btn_frame = tk.Frame(self.main_frame, bg="#1e1e2e")
        self.main_frame.pack(fill="both", expand=True)

        self.video_label = tk.Label(self.video_frame, bg="#44475a", width=640, height=480)
        self.video_label.pack(padx=20, pady=20)
        self.video_frame.grid_remove()

        btn_style = {"font": ("Arial", 12, "bold"), "width": 15, "padx": 5, "pady": 10}
        buttons = [
            ("▶ Start", "#50fa7b", "black", self.start_surveillance),
            ("⏹ Stop", "#ff5555", "white", self.stop_surveillance),
            ("➕ Add User", "#8be9fd", "black", self.add_user),
            ("❌ Remove User", "#bd93f9", "black", self.remove_user),
            ("📂 Intruder", "#f1fa8c", "black", self.open_intruder_folder)
        ]

        for text, bg, fg, cmd in buttons:
            btn = tk.Button(self.btn_frame, text=text, bg=bg, fg=fg, command=cmd, **btn_style)
            btn.pack()
            if text == "⏹ Stop":
                self.stop_btn = btn

            if text == "▶ Start":
                self.start_btn = btn

        self.btn_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.status_label = tk.Label(self.master, text="Status: Idle",
                                     font=("Arial", 12), bg="#1e1e2e", fg="#f8f8f2")
        self.status_label.pack(pady=10)

    def start_surveillance(self):
        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_label.config(text="Status: Surveillance running...")

        self.btn_frame.place_forget()
        self.video_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nw")
        self.btn_frame.grid(row=0, column=1, padx=30, pady=20, sticky="ne")
        self.capture_frames()

    def stop_surveillance(self):
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="Status: Surveillance stopped.")

        self.video_frame.grid_remove()
        self.btn_frame.grid_remove()
        self.btn_frame.place(relx=0.5, rely=0.5, anchor="center")

    def capture_frames(self):
        if not self.running:
            return

        try:
            stream = urllib.request.urlopen(ESP32_CAM_URL)
            bytes_data = bytearray(stream.read())
            frame = cv2.imdecode(np.asarray(bytes_data, dtype=np.uint8), -1)
        except:
            print("Failed to load from ESP32-CAM.")
            self.master.after(100, self.capture_frames)
            return

        if frame is not None:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            small_rgb = cv2.resize(rgb, (0, 0), fx=0.25, fy=0.25)
            face_locations = face_recognition.face_locations(small_rgb)
            face_encodings = face_recognition.face_encodings(small_rgb, face_locations)

            for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
                name = "Intruder"
                color = (0, 0, 255)

                if self.known_encodings:
                    distances = face_recognition.face_distance(self.known_encodings, encoding)
                    best_match = np.argmin(distances)
                    if distances[best_match] < FACE_MATCH_THRESHOLD:
                        name = self.known_names[best_match]
                        color = (0, 255, 0)

                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

                if name == "Intruder":
                    timestamp = int(time.time())
                    filepath = os.path.join(INTRUDER_FOLDER, f"intruder_{timestamp}.jpg")
                    cv2.imwrite(filepath, frame)
                    send_telegram_alert(filepath)

            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.master.after(10, self.capture_frames)

    def add_user(self):
        messagebox.showinfo("Info", "ESP32-CAM feed will open. Press 's' to save photo or 'q' to cancel.")

        while True:
            try:
                stream = urllib.request.urlopen(ESP32_CAM_URL)
                bytes_data = bytearray(stream.read())
                frame = cv2.imdecode(np.asarray(bytes_data, dtype=np.uint8), -1)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to access ESP32-CAM.\n{e}")
                return

            if frame is None:
                continue

            cv2.imshow("Capture New User - Press 's' to Save, 'q' to Cancel", frame)
            key = cv2.waitKey(1)

            if key & 0xFF == ord('s'):
                cv2.destroyAllWindows()
                username = simpledialog.askstring("Input", "Enter the user's name:")
                if username:
                    save_path = os.path.join(IMAGE_FOLDER, f"{username}.jpg")
                    cv2.imwrite(save_path, frame)
                    messagebox.showinfo("Success", f"User '{username}' added successfully!")
                    self.known_images, self.known_names = load_images()
                    self.known_encodings = encode_faces(self.known_images)
                else:
                    messagebox.showwarning("Warning", "Username cannot be empty.")
                break

            elif key & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break

    def remove_user(self):
        username = simpledialog.askstring("Input", "Enter the username to remove:")
        if not username:
            messagebox.showwarning("Warning", "Username cannot be empty.")
            return

        file_path = os.path.join(IMAGE_FOLDER, f"{username}.jpg")
        if os.path.exists(file_path):
            os.remove(file_path)
            messagebox.showinfo("Success", f"User '{username}' removed successfully!")
            self.known_images, self.known_names = load_images()
            self.known_encodings = encode_faces(self.known_images)
        else:
            messagebox.showerror("Error", f"No image found for user '{username}'.")

    def open_intruder_folder(self):
        os.startfile(INTRUDER_FOLDER)


if __name__ == "__main__":
    root = tk.Tk()
    app = FaceSurveillanceApp(root)
    root.mainloop()
