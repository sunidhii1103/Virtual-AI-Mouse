# 🖱️ Virtual AI Mouse – Gesture Controlled System

A computer vision-based desktop application that enables users to control their computer using real-time hand gestures instead of a traditional mouse.

The application captures live video from a webcam, detects hand landmarks using **MediaPipe**, processes gestures using **OpenCV**, and translates them into mouse and system actions using **PyAutoGUI**. This project demonstrates the application of Artificial Intelligence, Computer Vision, and Human-Computer Interaction (HCI) to create a touchless interface for desktop navigation.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Project Architecture](#-project-architecture)
- [Gesture Recognition](#-gesture-recognition)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [Future Enhancements](#-future-enhancements)
- [Documentation](#-documentation)
- [License](#-license)

---

# 📖 Overview

The Virtual AI Mouse replaces conventional mouse interactions with intuitive hand gestures captured through a webcam.

Using MediaPipe's 21-point hand landmark detection model, the application continuously tracks hand movement, recognizes predefined gestures, and performs corresponding operating system actions such as:

- Cursor movement
- Mouse clicks
- Drag and Drop
- Scrolling
- Zoom In / Zoom Out
- Presentation slide navigation
- Volume control 
- Brightness control 

The project emphasizes modular software architecture, real-time processing, and smooth user interaction.

---

# 🚀 Features

### 🖐️ Hand Tracking

- Real-time hand detection
- 21-hand landmark extraction
- Multi-point landmark visualization
- Bounding box rendering

### 🖱️ Mouse Control

- Cursor movement
- Left click
- Right click
- Double click
- Drag and Drop

### 📜 Navigation

- Vertical scrolling
- Horizontal scrolling *(optional)*
- Presentation slide control

### 🔍 Gesture Controls

- Zoom In
- Zoom Out

### ⚙️ Optional System Controls

- System Volume Control
- Screen Brightness Control

### 📊 Performance

- Real-time gesture recognition
- Cursor smoothing
- Coordinate interpolation
- FPS monitoring

---

# 🛠️ Technology Stack

| Category | Technologies |
|----------|--------------|
| Programming Language | Python |
| Computer Vision | OpenCV |
| Hand Tracking | MediaPipe |
| Mouse Automation | PyAutoGUI |
| Numerical Computing | NumPy |
| Volume Control  | Pycaw |
| Brightness Control | screen-brightness-control |

---

# 🏗️ Project Architecture

```
Webcam
    │
    ▼
OpenCV Camera Capture
    │
    ▼
MediaPipe Hand Detection
    │
    ▼
21 Hand Landmark Extraction
    │
    ▼
Gesture Recognition Engine
    │
    ▼
Mouse Controller (PyAutoGUI)
    │
    ▼
Operating System Actions
```

---

# ✋ Gesture Recognition

The gesture recognition engine determines finger states using the following format:

```
[Thumb, Index, Middle, Ring, Pinky]

1 = Finger Extended
0 = Finger Folded
```

## ✋ Gesture Recognition Matrix

The gesture recognition engine evaluates finger positioning in real time and maps specific hand configurations to native operating system triggers:

| Gesture Shape | Detected System State | Hardware Action / Executed Event |
| :--- | :--- | :--- |
| **Index Finger + Thumb Out** | `MOUSE_MOVE` | Absolute desktop cursor navigation via Index tip. |
| **All Fingers Curled Close** | `CLICK_LEFT` | Standard Left-Click / Selection trigger. |
| **Index + Middle Extended** | `CLICK_RIGHT` | Standard Right-Click context menu drop-down. |
| **Five Fingers Fully Open** | `PAGE_NAV` | Hand Wave Vertical Translation $\rightarrow$ Page Up / Page Down. |
| **Closed Fist / Small Cluster** | `SLIDE_NEXT` | Injects macro pulse to advance presentation slides. |
| **Downward Finger Arc / Droop** | `SLIDE_PREV` | Injects macro pulse to revert presentation slides. |
| **Rigid L-Shape / Pistol Shape** | `BRIGHTNESS_CONTROL` | Slides your Windows panel backlight brightness up/down. |
| **Three Fingers Extended** | `VOLUME_CONTROL` | Slides your native Windows master audio mixer up/down. |
| **Dynamic 2-Finger Pinch** | `ZOOM_PINCH` | Pinch expansion/contraction $\rightarrow$ Universal `Ctrl + Mouse Wheel`. |

> ⚠️ **Important:** The system defaults to an evaluation mode (`Status: OS Controls Disabled`) upon execution. Use your dedicated runtime hotkey toggle to switch the framework to **Active** mode to allow `PyAutoGUI` and native subprocess hooks to take command of your system peripherals.

> **Note:** Gesture mappings can be customized within the gesture recognition module.

---

# 📂 Project Structure

```
Virtual-AI-Mouse/
├── config/
│   └── settings.py          # Frame interpolation boundaries & dead-zone buffers
├── core/
│   ├── camera_module.py     # OpenCV capture window & FPS overlay matrices
│   ├── gesture_recognizer.py# Landmark spatial calculators & state transitions
│   └── controller.py        # PyAutoGUI macro executors & PowerShell driver hooks
├── tests/
│   └── test_gesture_recognizer.py # Verification assertion scripts (20/20 Passing)
├── models/
│   └── hand_landmarker.task # MediaPipe tracking weight configuration asset
├── main.py                  # Core runtime orchestration script
├── CODE_STATE.md            # Internal roadmap log tracker
├── requirements.txt         # Package dependency manifestations
└── README.md                # Project documentation
```

---

# 💻 Installation

## Prerequisites

- Python 3.10 or later
- Webcam
- Windows / Linux / macOS

---

## Clone the Repository

```bash
git clone https://github.com/sunidhii1103/Virtual-AI-Mouse.git

cd Virtual-AI-Mouse
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

or install manually

```bash
pip install opencv-python mediapipe pyautogui numpy
```

Optional packages

```bash
pip install pycaw

pip install screen-brightness-control
```

---

# ▶️ Usage

Run the application

```bash
python src/main.py
```

The application will

1. Open the webcam.
2. Detect hand landmarks.
3. Recognize hand gestures.
4. Execute the corresponding mouse or system action.

---

# 🧪 Testing

If test cases are available

```bash
pytest tests/
```

---

# 📈 Future Enhancements

- Multi-hand support
- Custom gesture creation
- Voice assistant integration
- Performance analytics dashboard

---

# 📚 Documentation

Additional project documentation is available in the **docs/** directory.

| File | Description |
|------|-------------|
| **PRD.md** | Product Requirements Document |
| **SRS.md** | Software Requirements Specification |
| **Architecture.md** | System Architecture |
| **AGENTS.md** | AI Development Guidelines |

---

# 🤝 Contributing

Contributions, suggestions, and feature requests are welcome.

Feel free to fork the repository, create a feature branch, and submit a pull request.

---

# 📄 License

This project is licensed under the MIT License.

---

## 👩‍💻 Author

**Sunidhi Pandey**

B.Tech Computer Science Engineering
