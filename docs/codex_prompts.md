# Codex Deployment Prompt Pack

This document captures a set of modular Codex-ready prompts for provisioning the Pi-Ops and Pi-Holo stack along with associated control interfaces. Each prompt is scoped to a single component so they can be run independently or stitched together as needed. Use this pack when you need a quick hand-off to an LLM or automation agent—every prompt spells out the exact files to emit so the resulting artifacts can be dropped straight into version control.

## Prompt Index

| # | Target | Primary outputs | Notes |
|---|--------|-----------------|-------|
| 1 | Pi-Ops MQTT broker | Bash installer + Mosquitto config | Boots the core message bus for lab deployments. |
| 2 | Arduino UNO firmware | `firmware.ino` sketch | Bridges environment sensors + command handling. |
| 3 | Serial↔MQTT bridge | Python service, systemd unit, installer | Moves sensor data into MQTT and forwards UI commands back. |
| 4 | Pi-Holo OpenGL renderer | CMake project | Provides the realtime holographic preview. |
| 5 | Pi-Holo video fallback | systemd unit + enable script | Guarantees visual output even without the renderer. |
| 6 | Control panel web app | HTML/CSS/JS bundle | Human interface for monitoring + commands. |
| 7 | Chromium kiosk | systemd unit + deploy script | Locks Pi-Ops into kiosk mode for the control app. |
| 8 | Touch mapping script | Bash utility | Maps touchscreens to the correct displays. |
| 9 | Jetson Orin API | FastAPI service bundle | REST bridge into the MQTT spine. |
| 10 | Message schema | JSON Schema | Ensures consistent cross-component payloads. |
| 11 | Heartbeat publisher | Python service, systemd unit, installer | Provides infra health telemetry. |
| 12 | Repo bootstrap | Bash scaffold script | Creates the workspace skeleton for collaboration. |

## Prompt 1 — MQTT broker on Pi-Ops
```
You are writing a Bash script and a Mosquitto config.
Output two files only:
1. setup_mosquitto.sh – a bash script that installs mosquitto and mosquitto-clients on Debian/Raspberry Pi OS, writes /etc/mosquitto/conf.d/lab.conf, enables and starts the service. Use set -euo pipefail.
2. lab.conf – mosquitto config that:
   • Listens on 0.0.0.0:1883
   • allow_anonymous true (lab only)
   • Sets persistence true, persistence_location /var/lib/mosquitto/
   • Reasonable message_size_limit (2MB)
Do not add explanations—only the two files’ content.
```

## Prompt 2 — Arduino UNO sensor/actuator firmware
```
Generate a complete Arduino sketch named firmware.ino for an Uno:
• DHT11 on pin 2, PIR on pin 3.
• Every 1000 ms, read temp (°C), humidity (%), PIR (0/1).
• Print one line per sample as compact JSON: {"ts":<ms>,"temp":23.4,"hum":45,"motion":1}
• Serial 115200.
• Accept ASCII commands terminated by \n: LED ON, LED OFF, PING (reply {"pong":true}). Use built-in LED 13.
• Debounce PIR (200 ms).
• Use DHT.h library with sensible error handling (NaN → omit field).
Output only the sketch.
```

## Prompt 3 — Pi-Ops serial↔MQTT bridge (+systemd)
```
Create four files:
1. bridge.py – Python 3 script using paho-mqtt and pyserial.
   • Read from /dev/ttyACM0 115200, parse each JSON line; publish to topics: sensors/temp, sensors/hum, sensors/motion (retain last). Also republish the raw line to sensors/raw.
   • Subscribe to ui/cmd and holo/cmd; on message, write the payload plus \n to serial.
   • Broker host from env MQTT_HOST (default localhost). Reconnect robustly.
2. requirements.txt – paho-mqtt and pyserial pins.
3. bridge.service – systemd unit to run bridge.py with Environment=MQTT_HOST=localhost, Restart=always, After=network-online.target.
4. install.sh – bash that creates a venv at /opt/bridge, installs deps, deploys service, enables/starts.
No explanations; only code.
```

## Prompt 4 — Pi-Holo OpenGL quadrant renderer
```
Output a minimal C++17 project that builds on a Raspberry Pi with SDL2 + OpenGL ES 2.0:
• Files: CMakeLists.txt, src/main.cpp, README.md.
• Fullscreen window on the default HDMI display.
• Render a spinning cube with dark background; render 4 views (front/right/back/left) using 4 view matrices.
• Pack into a single framebuffer as a 2×2 grid (top-left=front, top-right=right, bottom-left=back, bottom-right=left).
• Command line flags: --fps N, --size WxH, --invert (flip vertical if needed).
• ESC or SIGINT quits cleanly.
• README.md lists apt build deps and cmake … commands.
Output only those three files.
```

## Prompt 5 — Pi-Holo video fallback (mpv loop)
```
Produce two files:
1. autoplay.service – systemd unit that launches mpv --fs --no-osd-bar --loop-file=inf /home/pi/holo.mp4 on tty1 after network and local-fs, Restart=always.
2. enable.sh – bash to install the unit for user pi, systemctl enable --now.
Only code, no explanations.
```

## Prompt 6 — Control panel web app (kiosk)
```
Output a static web app with these files:
• index.html (semantic HTML; viewport meta)
• style.css (responsive layout: left rail 80px, content area, status bar)
• app.js (uses mqtt.min.js via CDN to connect to ws://<broker>:9001; subscribe sensors/#; publish to ui/cmd and holo/cmd on button clicks).
Features:
• Left rail: buttons Home, Scene 1, Scene 2, Pause, Resume (data-cmd attributes).
• Top badges show temp, hum, motion with color thresholds (e.g., red if motion=1).
• A small log console of last 10 events.
• app.js takes MQTT_URL from ?broker= query or defaults to ws://localhost:9001.
Output only those three files.
```

## Prompt 7 — Chromium kiosk autostart (Pi-Ops)
```
Create two files:
1. kiosk.service – systemd unit running as user pi, ExecStart launches /usr/bin/chromium --kiosk --app=http://localhost/index.html --incognito --noerrdialogs --disable-translate --check-for-update-interval=31536000.
2. deploy.sh – bash that copies the web app to /var/www/control, installs lighttpd serving that dir, enables kiosk.service (Wait for graphical target).
Only code.
```

## Prompt 8 — Touch mapping script (X11)
```
Output map_touch.sh:
• Bash that: lists input devices (xinput), finds touchscreen IDs by matching “touch” (case-insensitive), lists connected monitors via xrandr, and interactively prompts the user to map each touch device to a chosen monitor using xinput --map-to-output.
• Also prints a sample snippet to add to .xprofile for auto-mapping by exact device/monitor names.
Script must be idempotent and echo the final mapping table.
Code only.
```

## Prompt 9 — Jetson Orin workspace API (FastAPI)
```
Generate a FastAPI app with uvicorn runner:
Files: app/main.py, app/requirements.txt, app/run.sh, app/service.sh.
• Endpoints: GET /health, GET /sensors (cache of latest values pulled from MQTT), POST /holo with JSON {cmd:"SCENE_1"} → publishes to holo/cmd.
• Background MQTT client (paho) keeps an in-memory dict of last sensor values.
• CORS enabled for the control panel.
• run.sh launches uvicorn on 0.0.0.0:8080.
• service.sh creates a systemd unit to run on boot.
No explanations; only the four files.
```

## Prompt 10 — Common message schema (JSON)
```
Output a single file schema.json containing a JSON Schema Draft-07 for our message envelope:
• Required fields: trace_id (uuid), ts (RFC3339), source (string), type (enum: sensor, ui_cmd, holo_cmd, status), and either data (object) or message (string).
• Include examples for: sensor temp, UI command, holo command, and status heartbeat.
Only the schema file content.
```

## Prompt 11 — Heartbeat publisher
```
Create heartbeat.py: Python script using psutil and paho-mqtt that publishes every 10s to system/heartbeat/<hostname> with JSON: uptime (sec), loadavg, cpu%, mem%, ts, source. Broker from MQTT_HOST env. Provide a heartbeat.service unit and install.sh. Output those three files only.
```

## Prompt 12 — Repo bootstrap
```
Output a bash script bootstrap.sh that creates this tree and placeholder READMEs:
./arduino/
./pi-ops/{bridge,web,kiosk,heartbeat}/
./pi-holo/{gl,video}/
./jetson/{api,heartbeat}/
./docs/
Then prints next commands to run (in order) to deploy each piece. Script must be safe to re-run.
```

## Bundling Guidance
These prompts are intentionally modular so you can target the exact component you need without overwhelming the model context window. Reach for a single prompt when you are iterating on a component in isolation (for example, swapping in a different visualization in Prompt 4 or tweaking the kiosk startup in Prompt 7). When you need multiple components at once, prefer chaining them in the following order so shared assumptions line up:

1. **Bootstrap + MQTT core** → Prompts 12, 1, and 11 establish the repo layout, broker, and telemetry so everything downstream has a place to land.
2. **Edge capture path** → Prompts 2 and 3 wire the Arduino telemetry into the broker.
3. **Visualization layers** → Prompts 4, 5, 6, 7, and 8 unlock the UI and display flows; pick only the pieces required for your deployment tier.
4. **Northbound integrations** → Prompt 9 exposes the API surface and Prompt 10 enforces message structure.

If you ever need an "all-in-one" bootstrap, compose a higher-level wrapper that simply concatenates the relevant prompt blocks above while preserving their headings. This keeps the context clear to Codex (or any downstream assistant) and makes it easy to swap individual modules in or out without rebuilding the entire prompt from scratch.
