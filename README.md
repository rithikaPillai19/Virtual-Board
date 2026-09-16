# Virtual Screen Board: Touchless Air Canvas with Dual-Hand Multimodal Gesture Tracking & State Latching

[![Vercel Deployment](https://img.shields.io/badge/Vercel-Live%20Demo-brightgreen?logo=vercel)](https://virtual-board.vercel.app)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.14-orange)](https://developers.google.com/mediapipe)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

Virtual Screen Board is an interactive computer vision application that transforms an ordinary webcam into a touchless digital whiteboard. Traditional single-hand vision canvases suffer from the "clutch and tailing" dilemma—accidental strokes created while moving between points or pinching fingers. 

This system resolves that problem using a **Decoupled Asymmetric Dual-Hand Architecture**:
- **Left Hand (Command Deck / State Clutch):** Flashes brief gestures to lock operational modes (`DRAW`, `HOVER/STOP`, `ERASER`, `COLOR_SELECT`).
- **Right Hand (Analog Stylus):** Functions as the continuous pointing and inking pen using index fingertip kinematics.
- **State Latching (Sticky Modes):** Mode switches persist after a quick gesture flash, allowing users to drop their left hand to rest and draw completely hands-free without arm fatigue ("Gorilla Arm" syndrome).

The project is built with a dual-delivery model: a high-performance **desktop OpenCV/Python pipeline** and a zero-install **web client** running client-side WebAssembly deployed on Vercel.

---

## Key Features

- **Hands-Free State Latching:** Flash a gesture once with your left hand to lock into drawing, erasing, or palette selection; no need to keep both arms raised.
- **Dedicated 3-Finger Stop Inking:** Flash three fingers (Index + Middle + Ring) on your left hand to lift the digital pen into `HOVER` mode instantly.
- **Decoupled Dual-Hand Control:** Eliminates drawing tails and accidental strokes caused by single-hand pinching.
- **Non-Destructive Alpha Masking:** Blends digital ink layers with live camera streams using dynamic inverted binary masks.
- **Interactive Spatial Palette:** Real-time collision detection for selecting brush colors (`RED`, `GREEN`, `BLUE`, `YELLOW`) or clearing the canvas (`CLEAR`).
- **Dual-Platform Architecture:** Runs locally via Python/OpenCV or directly in modern web browsers via MediaPipe WebAssembly.
- **Zero-Footprint Privacy:** All visual frames and landmark matrices are computed on the client machine; no video data is sent to external servers.

---

## Left-Hand Gesture Control Matrix

| Left Hand Gesture (Flash Once) | Locked System State | Right Hand Stylus Behavior |
| :--- | :--- | :--- |
| **Thumb Only Up 👍** | `LOCKED: DRAW` | Inks smooth strokes wherever the right index finger moves. |
| **Three Fingers Up ✋₃** | `LOCKED: HOVER` | **Stops inking immediately**; displays an aiming reticle. |
| **All 5 Fingers Open 🖐️** | `LOCKED: ERASER` | Erases strokes under a 35px circular radius. |
| **Two Fingers Up ✌️** | `LOCKED: COLOR_SELECT` | Move right index finger to top-right toolbar buttons. |

---

## Technologies & Tools Used

- **Computer Vision & Machine Learning:** MediaPipe Hands (Palm Detection + 21 3D Skeletal Landmark Regressor)
- **Desktop Runtime:** Python 3.10+, OpenCV (`cv2`), NumPy
- **Web Runtime:** HTML5 Canvas, Vanilla CSS3, JavaScript (ES6+), MediaPipe JavaScript API
- **Deployment & Cloud:** Vercel (Edge Network Static Hosting), Git/GitHub
- **Testing Framework:** Python standard `unittest`

---

## Project Structure

```text
Virtual-Board/
├── .gitignore               # Excludes virtual environments and build cache
├── .vercelignore            # Configures static client build for Vercel
├── vercel.json              # Vercel deployment routing configuration
├── requirements.txt         # Pinned Python package dependencies
├── desktop_run.py           # Desktop orchestrator (OpenCV & FSM loop)
├── index.html               # Web interface markup & canvas layers
├── style.css                # Layout styling, camera mirroring, and HUD
├── app.js                   # Client-side web camera loop & drawing engine
├── statement.md             # Formal project problem statement & scope
├── src/
│   ├── __init__.py          # Python package marker
│   ├── hand_detector.py     # Skeletal landmark detection & pose classification
│   ├── canvas.py            # Canvas matrix manipulation, strokes, and blending
│   └── ui.py                # Toolbar interface & collision hit-testing
└── tests/
    └── test_canvas.py       # Automated unit tests for canvas & UI hitboxes