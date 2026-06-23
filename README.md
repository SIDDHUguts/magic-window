# Magic Window Filter · Interactive 3D Gesture & Synth Installation

A real-time, full-screen webcam "Magic Window" installation built using **HTML5 Canvas**, **MediaPipe JS Hands**, and **Web Audio API**. The application tracks your hands to project a fanning triangular prism filter beam, reacting dynamically with visual and synthesized audio effects.

This project is fully client-side, zero-dependency, and ready to be hosted for free on **GitHub Pages**.

---

## Features

- **Full-Screen Viewport & Aspect Ratio Cover:** The webcam feed scales and crops dynamically to cover the entire browser viewport (100vw/100vh) without warping.
- **Triangular Prism Beam:**
  - Pinch the thumb and index finger of **one hand** together to define the vertex (tip) of the beam.
  - Spread the thumb and index of your **other hand** to define the fanning base of the beam.
  - The magic window becomes a triangular spotlight that stretches, rotates, and fans dynamically as you move!
- **Interactive Sci-Fi Synthesizer Drone:** Synthesizes an ambient retro-futuristic sound drone mapped to hand positioning:
  - **Pitch (Frequency):** Mapped to the vertical height of your vertex hand. Move it up for a high pitch, down for a deep bass drone.
  - **Timbre (Filter Cutoff):** Mapped to the fanning width of your base hand. Spreading your fingers opens the filter (buzzy/sharp), pinching closes it (warm/subtle).
  - **Loudness (Gain):** Modulated by your hands' depth/closeness to the webcam.
- **Glassmorphic Floating Dashboard:** A HUD panel overlay for system diagnostics (live FPS, hand tracking markers) and interactive toggles (mute sound, hide skeletons, direct preset selection grid).
- **Collapsible Layout:** Press **`D`** or click "Hide Controls" to collapse the HUD panel into a clean screen, allowing a 100% immersive installation view.
- **Energy Beam Particles:** Spawn particle streams at the tip of the triangle that flow down the prism beam. Sparks also spray off the base when moving. Spark colors shift to match the active filter preset.
- **Preset Transition Flash:** A visual digital chromatic flicker overlay flashes whenever you switch presets, creating responsive visual feedback.

---

## 🎨 Visual Filter Presets

The triangle is split into three equal fanning sectors, each running separate image-processing shaders:

1. **Spectrum Halftone:** Top = Blue Halftone Dot Matrix, Middle = Thermal Infrared Heatmap, Bottom = Red Halftone Dot Matrix.
2. **Cyber Metal:** Top = Topographical Emboss, Middle = Cyber Neon Edge Detection, Bottom = Inverted X-Ray.
3. **Digital Matrix:** Top = Green ASCII code-rain style character terminal, Middle = Thermal Infrared, Bottom = Cyber Neon.
4. **Synthwave Glitch:** Top = Chromatic Aberration/Glitch with horizontal scanline noise, Middle = Hue-shifting Cyber Neon spectrum grid, Bottom = Retro 8-bit Pixelate.

---

## ⚙️ Controls & Shortcuts

| Input | Action |
| --- | --- |
| **Pinch (1 Hand) + Spread (Other Hand)** | Draw, rotate, and scale the fanning triangular prism |
| **Touch Index + Middle Tips** | Press fingers together on either hand to cycle presets |
| **Click / Tap Canvas** | Cycle presets |
| **Press `SPACE` or `C`** | Cycle presets |
| **Press `H` or `h`** | Toggle Hand skeleton tracking overlay (Guides: Show/Hide) |
| **Press `M` or `m`** | Toggle Web Audio Synthesizer sound (Mute/Unmute) |
| **Press `D` or `d`** | Toggle controls dashboard collapse (Minimize/Restore HUD) |

---

## 🚀 How to Run Locally

1. Install [Node.js](https://nodejs.org/).
2. Open your terminal inside the project directory and start the static file server:
   ```bash
   node server.js
   ```
3. Open your web browser and go to:
   👉 **[http://localhost:3000](http://localhost:3000)**
4. Allow webcam access, hold up your hands, and click the **"Sound"** button in the top right to start the synth!

---

## 🌐 How to Publish to GitHub Pages (Free Hosting)

Since this application is built entirely in browser-native JavaScript and HTML5, you can publish it live on the web in seconds using **GitHub Pages**:

1. Log in to your GitHub account and create a new repository named `magic-window`.
2. Open a terminal inside this directory and run the following commands to commit the code:
   ```bash
   git init
   git add .
   git commit -m "Initialize Magic Window full-screen audio installation"
   ```
3. Link your local project to your newly created GitHub repository:
   ```bash
   git branch -M main
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/magic-window.git
   git push -u origin main
   ```
   *(Be sure to replace `YOUR_GITHUB_USERNAME` with your actual GitHub username).*
4. Enable hosting:
   - Go to your repository page on GitHub.
   - Click the **Settings** tab.
   - On the left sidebar, click **Pages**.
   - Under **Build and deployment**, set the Source branch to `main` (under `/root`) and click **Save**.
5. Within 1–2 minutes, your website will be live at:
   👉 **`https://YOUR_GITHUB_USERNAME.github.io/magic-window/`**
