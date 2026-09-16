### `statement.md`

```markdown
# Problem Statement and Project Scope

## 1. Problem Statement

Touchless air-drawing and visual annotation systems allow users to write or sketch on computer screens without physical markers or digitizing tablets. However, existing single-hand implementations face three fundamental limitations:

1. **The Spatial "Clutch" & Tailing Problem:** Single-hand gesture interfaces (such as pinching thumb and index to draw) inherently displace the physical index fingertip when making or breaking the pinch. This introduces severe optical parallax, shaky stroke origins, and unwanted connecting trails across the canvas when moving the hand between strokes.
2. **"Gorilla Arm" Muscular Fatigue:** Systems requiring users to hold both hands in the camera frame continuously cause severe shoulder and arm strain within minutes of use, making them impractical for lectures or meetings.
3. **High Latency & Cloud Dependence:** Many vision interfaces stream frames to cloud backends for heavy neural processing, introducing latency ($\ge 150\text{ ms}$) and requiring costly compute resources.

The **Virtual Screen Board** solves these issues by decoupling mode controls from the drawing stylus using an asymmetric dual-hand architecture with temporal state latching.

---

## 2. Scope of the Project

### In Scope
- **Edge Vision Inference:** Real-time 21-point hand landmark tracking at $\ge 30\text{ FPS}$ on consumer dual/quad-core CPUs.
- **Asymmetric Role Separation:** Partitioning the left hand as a discrete command clutch and the right hand as a continuous analog stylus.
- **State Latching (Sticky Modes):** Maintaining the drawing/erasing mode after a momentary left-hand pose, allowing the user to drop their left arm.
- **Dedicated Stop Trigger:** Instantly lifting the pen via a 3-finger left-hand gesture without resetting the canvas or exiting the workspace.
- **Non-Destructive Alpha Compositing:** Real-time layering of digital ink over webcam video feeds using bitwise matrix masking.
- **Cross-Platform Deployability:** Dual delivery via a native Python/OpenCV desktop runner and a client-side WebAssembly static web app on Vercel.

### Out of Scope
- Recognition of complex dynamic sign language or cursive character extraction (OCR).
- Multi-user collaborative drawing over WebRTC networks.
- Pressure-sensitive brush simulation (which requires depth/LiDAR hardware).

---

## 3. Target Users

- **Educators & Online Tutors:** Annotate diagrams, solve formulas, and point to slides during video lectures without touching hardware.
- **Corporate Presenters & Speakers:** Deliver touchless whiteboard walkthroughs during presentations.
- **Sterile & Industrial Operators:** Medical staff in surgical theaters or technicians in cleanrooms who require digital interaction without physical surface contact.
- **Students & Remote Collaborators:** Quickly sketch ideas and wireframes during remote study sessions.

---

## 4. High-Level Features

- **Hands-Free State-Latching Finite State Machine:** Debounced transitions for `DRAW`, `HOVER`, `ERASER`, and `COLOR_SELECT`.
- **Three-Finger Instant Pen Lift:** Clean, artifact-free transitions between writing and aiming.
- **Real-Time Visual Telemetry (HUD):** On-screen display indicating current mode and detected finger states.
- **Interactive Top-Right Color Palette:** Collision hit-testing for colors and canvas clears.
- **Zero-Install Web Deployment:** Full client-side browser execution hosted on Vercel.