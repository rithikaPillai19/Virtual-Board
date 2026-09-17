# Virtual Screen Board: Touchless Air Canvas with Dual-Hand Multimodal Gesture Tracking & State Latching

---

## 1. Project Overview

Virtual Screen Board is an interactive computer vision application which can convert an ordinary webcam into a touch-free screen board. The conventional one-handed vision canvas suffers from the "clutch and tailing" problem wherein unintended strokes are created while moving from one point to another and while pinching the fingers.

This system resolves that problem using a **Decoupled Asymmetric Dual-Hand Architecture**:

* **Left Hand (Command Deck / State Clutch):** Flashes brief gestures to lock operational modes (`DRAW`, `HOVER/STOP`, `ERASER`, `COLOR_SELECT`).
* **Right Hand (Analog Stylus):** Functions as the continuous pointing and inking pen using index fingertip kinematics.
* **State Latching (Sticky Modes):** Mode switches persist after a quick gesture flash, allowing users to drop their left hand to rest and draw completely hands-free without arm fatigue ("Gorilla Arm" syndrome).

The project features a dual-delivery model: a high-performance **desktop OpenCV/Python pipeline** and a zero-install **web client** running client-side WebAssembly deployed on Vercel.

---

## 2. Key Features

* **Hands-Free State Latching:** Flash a gesture once with your left hand to lock into drawing, erasing, or palette selection; no need to keep both arms raised.
* **Dedicated 3-Finger Stop Inking:** Flash three fingers (Index + Middle + Ring) on your left hand to lift the digital pen into `HOVER` mode instantly.
* **Decoupled Dual-Hand Control:** Eliminates drawing tails and accidental strokes caused by single-hand pinching.
* **Non-Destructive Alpha Masking:** Blends digital ink layers with live camera streams using dynamic inverted binary masks.
* **Interactive Spatial Palette:** Real-time collision detection for selecting brush colors (`RED`, `GREEN`, `BLUE`, `YELLOW`) or clearing the canvas (`CLEAR`).
* **Dual-Platform Architecture:** Runs locally via Python/OpenCV or directly in modern web browsers via MediaPipe WebAssembly.
* **Zero-Footprint Privacy:** All visual frames and landmark matrices are computed on the client machine; no video data is sent to external servers.

---

## 3. Left-Hand Gesture Control Matrix

| Left Hand Gesture (Flash Once) | Locked System State | Right Hand Stylus Behavior |
| --- | --- | --- |
| **Thumb Only Up 👍** | `LOCKED: DRAW` | Inks smooth strokes wherever the right index finger moves. |
| **Three Fingers Up ✋₃** | `LOCKED: HOVER` | **Stops inking immediately**; displays an aiming reticle. |
| **All 5 Fingers Open 🖐️** | `LOCKED: ERASER` | Erases strokes under a 35px circular radius. |
| **Two Fingers Up ✌️** | `LOCKED: COLOR_SELECT` | Move right index finger to top-right toolbar buttons. |

---

## 4. Technologies & Tools Used

* **Computer Vision & Machine Learning:** MediaPipe Hands (Palm Detection + 21 3D Skeletal Landmark Regressor)
* **Desktop Runtime:** Python 3.10+, OpenCV (`cv2`), NumPy
* **Web Runtime:** HTML5 Canvas, Vanilla CSS3, JavaScript (ES6+), MediaPipe JavaScript API
* **Deployment & Cloud:** Vercel (Edge Network Static Hosting), Git/GitHub
* **Testing Framework:** Python standard `unittest`

---

## 5. Project Structure

```text
Virtual-Board/
├── .gitignore               # Excludes virtual environments and build cache
├── .vercelignore            # Configures static client build for Vercel
├── vercel.json              # Vercel deployment routing configuration
├── requirements.txt         # Pinned Python package dependencies
├── desktop_run.py           # Desktop orchestrator (OpenCV & FSM loop)
├── test.py                  # Standalone test runner script
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

```

---

## 6. System Requirements & Prerequisites

* **Hardware:** Standard laptop or desktop with an integrated or USB webcam ($1280 \times 720$ resolution recommended at $\ge 30\text{ FPS}$).
* **Python Runtime:** Python 3.10, 3.11, or 3.12 installed and added to PATH (`python --version` or `python3 --version`).
* **Web Browser (for web version):** Google Chrome, Microsoft Edge, Brave, or Mozilla Firefox with WebAssembly and webcam access enabled.

---

## 7. Setup and Installation

### Step 1: Clone the Repository

Open your terminal and clone the repository:

```bash
git clone [https://github.com/rithikaPillai19/Virtual-Board.git](https://github.com/rithikaPillai19/Virtual-Board.git)
cd Virtual-Board

```

### Step 2: Set Up an Isolated Virtual Environment

* **Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1

```


* **Windows (Command Prompt):**
```cmd
python -m venv venv
.\venv\Scripts\activate.bat

```


* **macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate

```



### Step 3: Install Required Dependencies

Ensure `pip` is updated, then install all pinned requirements:

```bash
pip install --upgrade pip
pip install -r requirements.txt

```

---

## 8. Configuration Notes

* **Camera Resource Lock:** Ensure no other application (Zoom, Microsoft Teams, Skype, Google Meet) is actively occupying camera index `0`.
* **Lighting:** Operates best in balanced ambient lighting ($150\text{ lx} - 650\text{ lx}$). Avoid placing high-intensity backlights directly behind hands.
* **Headless Notice:** The desktop script (`desktop_run.py`) uses an OpenCV visual window (`cv2.imshow`). If running on a remote headless terminal/server without an active display session, execute the unit test suite or access the live web build instead.

---

## 9. Execution Instructions

### Option A: Running the Desktop Application (Python)

Ensure your virtual environment is activated, then run:

```bash
python desktop_run.py

```

**Single-Line Chained Shortcut (Install + Launch):**

* **Windows (PowerShell):**
```powershell
pip install -r requirements.txt; python desktop_run.py

```


* **macOS / Linux:**
```bash
pip install -r requirements.txt && python desktop_run.py

```



**Runtime Controls:**

* Hold your hands within the camera frame.
* Flash **Left Thumb Up** to lock into `DRAW` mode.
* Point with your **Right Index Finger** to draw.
* Flash **Left 3-Fingers Up** to lift the pen into `HOVER` mode.
* Flash **Open Palm** to lock into `ERASER` mode.
* Press **`q`** on your keyboard while focused on the video window to terminate the application cleanly.

---

### Option B: Running the Web Application (Browser)

* **Instant Live Cloud Demo:** Open [https://virtual-board.vercel.app](https://virtual-board.vercel.app) in any modern browser.

---

## 10. Automated Testing & Validation

The project includes an automated test suite verifying matrix allocations, stroke interpolation, eraser clearing, alpha blending, UI hitboxes, and finger kinematics without opening a physical camera.

Run the test suite using either command from the root directory:

```bash
# Using standard unittest discover
python -m unittest discover -s tests

# Or using the root test runner script
python test.py

```

**Expected Test Output:**

```text
test_alpha_blend_compositing (tests.test_canvas.TestVirtualScreenBoard) ... ok
test_canvas_clear (tests.test_canvas.TestVirtualScreenBoard) ... ok
test_canvas_initialization (tests.test_canvas.TestVirtualScreenBoard) ... ok
test_finger_up_classification (tests.test_canvas.TestVirtualScreenBoard) ... ok
test_reset_point (tests.test_canvas.TestVirtualScreenBoard) ... ok
test_stroke_rasterization (tests.test_canvas.TestVirtualScreenBoard) ... ok
test_ui_button_collision (tests.test_canvas.TestVirtualScreenBoard) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.038s

OK

```
