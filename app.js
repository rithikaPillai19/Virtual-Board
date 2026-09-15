const videoElement = document.getElementById("webcam");
const paintCanvas = document.getElementById("paint-canvas");
const paintCtx = paintCanvas.getContext("2d");
const pointerCanvas = document.getElementById("pointer-canvas");
const pointerCtx = pointerCanvas.getContext("2d");

const statusMode = document.getElementById("status-mode");
const statusLeft = document.getElementById("status-left");
const buttons = document.querySelectorAll(".tool-btn");
const clearBtn = document.getElementById("clear-btn");

let currentColor = "#0000ff";
let prevPoint = null;

function resize() {
  paintCanvas.width = window.innerWidth;
  paintCanvas.height = window.innerHeight;
  pointerCanvas.width = window.innerWidth;
  pointerCanvas.height = window.innerHeight;
}
window.addEventListener("resize", resize);
resize();

buttons.forEach(btn => {
  btn.addEventListener("click", () => {
    if (btn.id === "clear-btn") {
      paintCtx.clearRect(0, 0, paintCanvas.width, paintCanvas.height);
      return;
    }
    buttons.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    currentColor = btn.getAttribute("data-color");
  });
});

function getFingersUp(landmarks) {
  const tipIds = [4, 8, 12, 16, 20];
  const fingers = [];

  // Thumb: tip (4) higher than IP joint (3)
  fingers.push(landmarks[4].y < landmarks[3].y ? 1 : 0);

  // Other 4 fingers: tip y < pip y
  for (let i = 1; i < 5; i++) {
    fingers.push(landmarks[tipIds[i]].y < landmarks[tipIds[i] - 2].y ? 1 : 0);
  }
  return fingers;
}

function onResults(results) {
  pointerCtx.clearRect(0, 0, pointerCanvas.width, pointerCanvas.height);

  let leftLms = null;
  let rightLms = null;

  if (results.multiHandLandmarks && results.multiHandedness) {
    for (let i = 0; i < results.multiHandLandmarks.length; i++) {
      const lms = results.multiHandLandmarks[i];
      const wristX = lms[0].x;
      // Mirror check: screen left vs screen right
      if (wristX > 0.5) {
        leftLms = lms;
      } else {
        rightLms = lms;
      }
    }
  }

  // 1. Evaluate Left Hand
  let leftMode = "HOVER";
  if (leftLms) {
    const lFingers = getFingersUp(leftLms);
    const count = lFingers.reduce((a, b) => a + b, 0);

    if (count >= 4) {
      leftMode = "ERASER";
    } else if (lFingers[0] === 1 && lFingers[1] === 1 && lFingers[2] === 1 && lFingers[3] === 0 && lFingers[4] === 0) {
      leftMode = "COLOR_SELECT";
    } else if (lFingers[0] === 1 && lFingers[1] === 0 && lFingers[2] === 0 && lFingers[3] === 0 && lFingers[4] === 0) {
      leftMode = "DRAW";
    }
    statusLeft.textContent = `LEFT COMMAND: ${leftMode}`;
  } else {
    statusLeft.textContent = "LEFT COMMAND: NONE (HOVER)";
  }

  // 2. Execute Right Hand
  if (rightLms) {
    const rx = rightLms[8].x * pointerCanvas.width;
    const ry = rightLms[8].y * pointerCanvas.height;

    if (leftMode === "ERASER") {
      paintCtx.save();
      paintCtx.globalCompositeOperation = "destination-out";
      paintCtx.beginPath();
      paintCtx.arc(rx, ry, 35, 0, 2 * Math.PI);
      paintCtx.fill();
      paintCtx.restore();

      pointerCtx.strokeStyle = "#ff0000";
      pointerCtx.lineWidth = 3;
      pointerCtx.beginPath();
      pointerCtx.arc(rx, ry, 35, 0, 2 * Math.PI);
      pointerCtx.stroke();
      statusMode.textContent = "MODE: ERASING";
      prevPoint = null;

    } else if (leftMode === "COLOR_SELECT") {
      pointerCtx.fillStyle = "#ffffff";
      pointerCtx.beginPath();
      pointerCtx.arc(rx, ry, 10, 0, 2 * Math.PI);
      pointerCtx.fill();
      statusMode.textContent = "MODE: COLOR SELECT (CLICK TOP BAR)";
      prevPoint = null;

      // Tap detection for toolbar
      const screenX = pointerCanvas.width - rx; // mirror adjustment
      const elem = document.elementFromPoint(screenX, ry);
      if (elem && elem.classList.contains("tool-btn")) {
        elem.click();
      }

    } else if (leftMode === "DRAW") {
      if (prevPoint) {
        paintCtx.strokeStyle = currentColor;
        paintCtx.lineWidth = 6;
        paintCtx.lineCap = "round";
        paintCtx.beginPath();
        paintCtx.moveTo(prevPoint.x, prevPoint.y);
        paintCtx.lineTo(rx, ry);
        paintCtx.stroke();
      }
      prevPoint = { x: rx, y: ry };

      pointerCtx.fillStyle = currentColor;
      pointerCtx.beginPath();
      pointerCtx.arc(rx, ry, 8, 0, 2 * Math.PI);
      pointerCtx.fill();
      statusMode.textContent = "MODE: DRAWING";

    } else {
      pointerCtx.strokeStyle = "#ffff00";
      pointerCtx.lineWidth = 2;
      pointerCtx.beginPath();
      pointerCtx.arc(rx, ry, 6, 0, 2 * Math.PI);
      pointerCtx.stroke();
      statusMode.textContent = "MODE: HOVER / AIM";
      prevPoint = null;
    }
  } else {
    prevPoint = null;
  }
}

const hands = new Hands({
  locateFile: file => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
});

hands.setOptions({
  maxNumHands: 2,
  modelComplexity: 1,
  minDetectionConfidence: 0.75,
  minTrackingConfidence: 0.7
});
hands.onResults(onResults);

const camera = new Camera(videoElement, {
  onFrame: async () => {
    await hands.send({ image: videoElement });
  },
  width: 1280,
  height: 720
});
camera.start();