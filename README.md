# Smart Surveillance System

An IoT-based home security system using **ESP32-CAM** for live face detection and real-time alerts via **Telegram**. With a simple Python GUI, users can start surveillance, manage known faces, and capture intruder footage — all from one desktop interface.

---

## How It Works

- ESP32-CAM streams live video over Wi-Fi.
- Face recognition detects known or unknown people.
- If an **unknown face** is detected:
  - It captures the image
  - Sends an alert with the photo to your **Telegram** chat
- A custom **Tkinter GUI** lets you:
  - Add/remove known users
  - Start/stop surveillance
  - View saved intruder images
  - Record activity manually


---

## Tech Stack

| Component       | Technology          |
|-----------------|---------------------|
| Hardware        | ESP32-CAM           |
| Programming     | Python              |
| Libraries       | OpenCV, face_recognition, Tkinter, PIL |
| Alerts          | Telegram Bot API    |
| Interface       | Desktop GUI (Tkinter) |

---

## Features

- Real-time face detection using ESP32-CAM
- Real-time image alerts via Telegram
- Easy user management via GUI 
- Motion-triggered image capture
