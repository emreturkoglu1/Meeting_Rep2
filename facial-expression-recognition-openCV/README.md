#  Real-Time Emotion Recognition with Webcam

A lightweight Python application that performs **real-time facial emotion recognition** using your webcam.  
It detects and classifies five basic emotions: **Neutral**, **Happy**, **Sad**, **Surprised**, and **Angry**.

This project leverages **MediaPipe's Face Mesh** for landmark detection and **OpenCV** for video capture and display.

---

##  Overview

This project analyzes facial landmarks in real-time and applies rule-based logic to estimate the user's current emotion.  
No deep learning model is used — it's fast, responsive, and easily customizable.

---

##  Features

- 📷 Real-time webcam capture
- 🧠 Emotion classification based on facial geometry
- 🚀 Runs locally, no internet or cloud processing required
- 📦 Clean and minimal dependencies
- 💡 Easily extendable with more rules or expressions

---

##  Detected Emotions

| Emotion   | Detection Cues |
|-----------|----------------|
| **Happy**     | Mouth slightly open |
| **Sad**       | Eyebrows lower and closer to eyes |
| **Surprised** | Wide-open eyes and mouth |
| **Angry**     | Inner brows close together |
| **Neutral**   | Default state |

---

---

##  Installation

### 1. Clone the repository

```bash
git clone https://github.com/ahmetbekir22/facial-expression-recognition-openCV.git

```

## How It Works
This project uses rule-based heuristics derived from the positions of facial landmarks:

Mouth openness is used to determine smiling or surprise.

Eye openness helps detect surprise.

Eyebrow-to-eye distance helps identify sadness.

Distance between inner eyebrows helps detect anger.

All distances are normalized by face height to ensure robustness across different face sizes and positions.