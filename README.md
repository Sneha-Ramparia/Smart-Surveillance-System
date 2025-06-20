# 🔒 Smart Surveillance System

An intelligent IoT-based home security project using **ESP32-CAM**, **face recognition**, and **Telegram alerts**. It detects unknown faces in real-time, sends image alerts to your phone, and provides a desktop GUI for full control — all built with open-source tools.

---

## 📸 How It Works

- 📷 ESP32-CAM streams live video over Wi-Fi.
- 🧠 Python-based face recognition checks for known faces.
- 🚨 Unknown face? It captures the frame and sends it to **Telegram**.
- 🖥 A user-friendly GUI lets you:
  - Add/remove users
  - Start/stop surveillance
  - View saved intruder images
  - Record video footage

---

## 💻 Tech Stack

| Component       | Technology          |
|-----------------|---------------------|
| Hardware        | ESP32-CAM           |
| Programming     | Python              |
| Libraries       | OpenCV, face_recognition, Tkinter, PIL |
| Alerts          | Telegram Bot API    |
| Interface       | Desktop GUI (Tkinter) |
| Deployment      | Local (No cloud needed) |

---

## 🧠 Features

- Motion-triggered face detection
- Real-time image alerts via Telegram
- One-click recording and user management
- Offline local processing (no cloud)
- Folder-based face recognition system
