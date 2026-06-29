🖱️ Virtual AI Mouse – Gesture Controlled System

A modular computer vision application that enables touchless desktop interaction using real-time hand gestures. The system uses MediaPipe for hand landmark detection, OpenCV for image processing, and PyAutoGUI to translate recognized gestures into native operating system actions such as cursor movement, clicking, scrolling, zooming, and presentation control.

🚀 Key Features
Real-Time Hand Tracking using MediaPipe's 21-hand landmark detection model.
Smooth Cursor Control through coordinate interpolation and cursor smoothing algorithms.
Gesture-Based Mouse Operations including left click, right click, double click, drag-and-drop, and scrolling.
Presentation Mode for slide navigation using predefined gestures.
Zoom Control using pinch gestures.
Optional System Controls for volume and brightness adjustment.
Modular Architecture with separate modules for hand tracking, gesture recognition, and mouse control.
Cross-Platform Python Implementation using standard open-source libraries.
🎮 Gesture Recognition Matrix

The gesture engine determines the state of each finger using a binary array:

[Thumb, Index, Middle, Ring, Pinky]

1 = Finger Extended
0 = Finger Folded
Gesture	Finger State	Action
☝️ Index Finger	[0,1,0,0,0]	Move Cursor
🤏 Thumb + Index Pinch	Distance Threshold	Left Click
✌️ Index + Middle	[0,1,1,0,0]	Scroll Mode
🤏 Index + Middle Pinch	Distance Threshold	Right Click
🤏 Thumb + Middle Pinch	Distance Threshold	Double Click
🤏 Thumb + Pinky Pinch	Distance Threshold	Drag & Drop
👍 Thumb Up	[1,0,0,0,0]	Next Slide
👎 Thumb Down	Thumb Orientation	Previous Slide
🖐️ Open Palm	[1,1,1,1,1]	Pause Cursor
🤏 Thumb–Index Distance	Continuous	Zoom In / Zoom Out

(The exact gesture mappings are configurable and can be modified within the gesture recognition module.)

🛠️ Project Architecture
Virtual-AI-Mouse/
│
├── docs/
│   ├── PRD.md
│   ├── SRS.md
│   ├── Architecture.md
│   └── AGENTS.md
│
├── src/
│   ├── main.py
│   ├── HandTrackingModule.py
│   ├── GestureRecognizer.py
│   ├── MouseController.py
│   └── utils.py
│
├── assets/
│   ├── images/
│   └── demo.mp4
│
├── tests/
│   └── test_gestures.py
│
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
💻 Installation
Prerequisites
Python 3.10 or later
Webcam
Windows/Linux/macOS
Clone Repository
git clone https://github.com/sunidhii1103/Virtual-AI-Mouse.git
cd Virtual-AI-Mouse
Install Dependencies
pip install -r requirements.txt

or

pip install opencv-python mediapipe pyautogui numpy

Optional:

pip install pycaw
pip install screen-brightness-control
▶️ Run the Application
python src/main.py

The application opens the webcam, detects hand landmarks in real time, recognizes gestures, and translates them into operating system actions.

🧪 Testing

Run the test suite (if available):

pytest tests/
📈 Future Enhancements
Multi-hand gesture support
User-configurable gesture mapping
Gesture recording and training
AI-based custom gesture recognition
Voice command integration
Cross-platform optimization
GUI settings panel
Performance profiling and FPS monitoring
📄 License

This project is licensed under the MIT License.
