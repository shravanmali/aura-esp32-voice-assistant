# Aura ESP32-S3 Voice Assistant & Telephony Bridge (v0)

Aura is a sub second multi-language smart voice assistant, & VoIP Telephony bridge that utilises the ESP32-S3 microcontroller with onboard wake-word detection, real-time AES, STT and LLM reasoning via Groq, Microsoft Neural / Cartesia TTS, and a 8bit WS2812 RGB LED status strip.

🌟 Features

⚡ Sub-Second Voice Response (<1100ms (Approx) End-to-End) - Uses Groq's fast LPU to provide low latency responses (qwen/qwen3.8-27b and whisper-large-v3-turbo).

🎛 Dual Core - ESP32-S3 with ESP-IDF 5.5.5 using Octal PSRAM @ 240MHz for high quality 16kHz I2S full duplex audio.

🛡 Acoustic Echo Suppression (AES) - Using a 550ms real time hardware hangover window to mute Microphone while playing caller's audio.

📞 Telephony Bridge (VoIP SIP) - Can make calls over Landline using SIP with JioFiber IMS. Just say "Alexa call Mom" or "Alexa call myself".

🌈 Aura 8-Bit WS2812 Light Effects - which is an responsive RGB LED that changes its colour according to the function live working on assistant.


## 💡 Aura 8-Bit RGB LED Status Patterns

| State | Visual Pattern | Color / Style | Trigger / Meaning |
| :--- | :--- | :--- | :--- |
| **Idle** | Completely Off | Black / Off | Standby, listening for wake word |
| **Listening** | Solid Glow | Bright Cyan / Teal | Wake word detected (`"Alexa"`), recording speech |
| **Thinking** | Color Wipe Animation | Cyan / Blue Wipe | Groq Whisper STT + LLM reasoning in progress |
| **Speaking** | Smooth Pulse | Indigo / Purple Pulse | MAX98357A speaker streaming TTS speech |
| **Ringing** | Fast Radar Sweep | Red / Amber Scanner | Outgoing call is ringing the recipient's phone |
| **In-Call** | Solid Steady Glow | Emerald Green | Call answered; two-way conversation active |
| **Muted** | Solid Red | Pure Red | ESP32 microphone muted / disabled |
| **Hangup** | Triple Blink & Fade | Crimson Red | Call ended / rejected / disconnected |

---

## 🛠️ Hardware Wiring & Pinout

### 1. ESP32-S3 DevKit-C (N16R8)

| Component | Component Pin | ESP32-S3 GPIO | Description |
| :--- | :--- | :--- | :--- |
| **INMP441 Mic** | VDD | 3.3V | Power supply |
| | GND | GND | Ground |
| | SD | GPIO 17 | I2S Serial Data In |
| | WS / LRCLK | GPIO 15 | I2S Word Select / Left-Right Clock |
| | SCK / BCLK | GPIO 16 | I2S Bit Clock |
| | L/R | GND | Left Channel Selection |
| **MAX98357A Amp** | VIN | 5V | 5V Power rail |
| | GND | GND | Ground |
| | DIN | GPIO 7 | I2S Serial Data Out |
| | LRC / LRCLK | GPIO 6 | I2S Word Select |
| | BCLK | GPIO 5 | I2S Bit Clock |
| | GAIN | Floating (or GND) | Default gain |
| | SD_MODE | Floating | Stereo-mix to Mono |
| **WS2812 8-Bit Strip** | 4-7VDC | 5V | Power Rail |
| | GND | GND | Common Ground |
| | DI (Data In) | GPIO 4 | RMT Output Channel |

---

## 📂 Project Architecture

```
.
├── voice_assistant.yaml           # ESPHome ESP-IDF firmware configuration
├── voice_server.py                # Main backend server (STT, LLM, TTS, Native API)
├── esp32_call_bridge.py           # Audio routing & Acoustic Echo Suppression (AES)
├── calling_test/
│   ├── app.py                     # Flask VoIP calling bridge service (Port 5050)
│   ├── jfc_configure.py           # Automated JioFiber SIP credential provisioner
│   ├── sip_client.py              # MicroSIP process wrapper & event monitor
│   ├── contacts.example.json      # Template for speed dial contacts
│   ├── jio_config.example.json    # Template for SIP credentials
│   └── templates/index.html       # Web dashboard for telephony management
├── local_secrets.example.py       # Template for API keys (Groq, Cartesia)
├── secrets.example.yaml           # Template for ESPHome Wi-Fi credentials
├── memory.example.json            # Template for persistent assistant memory
└── README.md                      # Documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites

- Python 3.10+ (Windows 10/11 recommended for MicroSIP telephony)
- Virtual Environment:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  pip install esphome aiohttp groq soundfile numpy comtypes flask requests
  ```
- [MicroSIP](https://www.microsip.org/) installed in `calling_test/microsip/` (if using VoIP features).

### 2. Configure Secrets

1. **ESPHome Wi-Fi**:
   ```powershell
   Copy-Item secrets.example.yaml secrets.yaml
   # Fill in your Wi-Fi SSID and Password in secrets.yaml
   ```

2. **API Keys**:
   ```powershell
   Copy-Item local_secrets.example.py local_secrets.py
   # Fill in your Groq API key(s) in local_secrets.py
   ```

3. **Contacts & VoIP**:
   ```powershell
   Copy-Item calling_test/contacts.example.json calling_test/contacts.json
   Copy-Item calling_test/jio_config.example.json calling_test/jio_config.json
   Copy-Item memory.example.json memory.json
   ```

### 3. Flash ESP32 Firmware

Compile and upload the firmware over USB or OTA:
```powershell
# First flash via USB:
esphome run voice_assistant.yaml --device COM3

# Or subsequent flashes over local Wi-Fi (OTA):
esphome upload voice_assistant.yaml --device 192.168.31.200
```

### 4. Run the Backend Servers

Start the calling bridge service:
```powershell
cd calling_test
python app.py
```

In a separate terminal, launch the main voice assistant daemon:
```powershell
python voice_server.py
```

---

## 📞 Telephony Voice Commands

- *"Alexa, call Mom"* &rarr; Resolves contact from `contacts.json` and initiates landline call.
- *"Alexa, call myself"* &rarr; Dials your personal phone number.
- *"Alexa, hang up"* / *"Alexa, disconnect"* &rarr; Ends the active VoIP call and restores normal assistant mode.

---

## 🛡️ License

MIT License. Designed and crafted with ❤️ for high-performance home automation and voice computing.



same PROJECT_STORY.md

                    !
                    !
                    !
                    !
                    !
                    1
                    !
                    ↓

# From Scratch to Reality 🚀

Building a voice assistant that actually talks back with the lowest latency possible using only 5 bare components and valuable software knowledge — pushing the ESP32 as a bare microprocessor to its absolute physical limits by adding a full-duplex telephony engine that dials real phone calls across the country with just a voice command. It doesn’t just dial the call; it seamlessly works as a real live telephone call directly through the ESP32!

*(Wake word is "Alexa" because I haven’t had time yet to train my own custom personal wake word, and the wake word "Alexa" is already pre-trained and pre-tuned.)*

---

## 📺 Live Video Demos & Proof in Action

Watch the live hardware running directly from our workbench:

* 🌦️ **Video 1: Sub-Second Multi-Intent Voice Query (Live Weather & Bitcoin Price)**  
  ▶️ [Watch on YouTube Shorts](https://youtube.com/shorts/PmZ0z8Imm-w)
* 📞 **Video 2: Live ESP32 VoIP Telephony Call ("Alexa, Call Myself" via Jio IMS SIP)**  
  ▶️ [Watch on YouTube Shorts](https://youtube.com/shorts/HGMN75dKRuE)
* 🧠 **Video 3: Autonomous Long-Term Memory & Identity Recall ("Registered on Stardance")**  
  ▶️ [Watch on YouTube Shorts](https://youtu.be/rkv8eTRfRxI)

---

## 1. The 5 Bare Components

1. **ESP32-S3 DevKitC-1** (16MB Flash, 8MB Octal PSRAM)
2. **INMP441** I2S MEMS Omnidirectional Microphone
3. **MAX98357A** I2S Class-D DAC & Amplifier
4. **4Ω 3W** Full-Range Acoustic Speaker
5. **WS2812B** 8-Pixel Addressable RGB LED Ring

*(Plus a standard breadboard and jumper wires — you don’t need that if you have a custom PCB made 😉)*

---

## 2. The Story — Approx. 65 Hours of Blood, Sweat & Code!

This project didn’t start today or yesterday. We started this journey weeks ago from absolute scratch (regardless of whether it shows 3h 35m as logged time!).

### Key Engineering Roadblocks Overcome:

1. **Noisy Audio & Electrical Hum:**  
   The microphone was constantly picking up a loud 50Hz electrical hum and DC bias noise, making speech hard to recognize. I solved this by adding an 85Hz digital high-pass filter and a 3.2kHz vocal presence boost in Python to make the voice razor-sharp.

2. **Speaker Glitches & ESP32 Crashes:**  
   Whenever Wi-Fi dropped even a single audio packet, the speaker would stutter and trigger a FreeRTOS watchdog crash. I fixed this by splitting the microphone and speaker into two separate I2S hardware buses so they never fight over data.

3. **Painfully Slow Response Delays:**  
   Standard DIY voice assistants take 3 to 5 seconds to reply, feeling slow and unnatural. By replacing heavy local pipelines with Groq LPUs (Whisper Turbo + fast neural TTS), I squeezed the full conversational reply down to a sub-second (~800–1200ms) turnaround.

And of course, so much more! 😭😭😭😭

---

<a id="part-2"></a>

## 3. Pushing ESP32 Silicon to Its Physical Limit: Full-Duplex Audio & Live Intelligence 🚀

We didn’t just build a basic voice trigger. We turned this tiny microcontroller into a living, full-duplex room presence that actively listens, adapts to ambient noise, dials real phone calls across the country, and fetches live data from the web in milliseconds.

### 📞 Feature 1: Two-Way VoIP Landline Telephony
* **Voice-Activated Dialing:** Saying "Alexa, call Mom" or "Call myself" parses the contact and instantly routes a live SIP call through Jio Fiber’s IMS exchange over secure TLS.
* **Live Speakerphone:** The remote caller’s voice streams out of the MAX98357A speaker with zero lag, while the INMP441 mic beams 16kHz HD Voice (AMR-WB) back to their smartphone.
* **Acoustic Echo Suppression (AES):** Intelligently ducks the room microphone when the remote party speaks, preventing feedback loops without dedicated DSP hardware.

### 🔊 Feature 2: Smart Acoustic Radar (Auto-Volume & Room Noise Sensing)
* **Room Noise Awareness:** Aura samples the ambient room noise floor before each response.
* **Dynamic Volume Scaling:** Automatically speaks softly in a quiet room at night, and boosts volume and vocal clarity if a fan or AC is humming loudly.
* **Zero Idle Hiss:** Audio drivers sleep during silence and wake seamlessly for audio streams, keeping the room completely silent when idle.

### 🌐 Feature 3: Real-Time Web Intelligence & Live Tools
* **Live Crypto & Market Data:** Ask "What's Bitcoin at?" to get live prices and real-time market movements on the fly.
* **Hyper-Local Weather:** Instant live temperature, precipitation forecasts, and humidity for our exact coordinates.
* **Offline Hardware Timers:** Hands-free timers with pleasant hardware chimes that trigger directly through the speaker even during Wi-Fi drops.
* **Seamless Multilingual Brain:** Automatically switches and responds in English, Hindi, Gujarati, or Marathi with expressive human-like neural voices.

### 🎙️ Feature 4: True Full-Duplex & Instant Barge-In (Beta Version)
* **Talk & Listen Simultaneously:** Dual dedicated I2S hardware buses allow the mic to listen while the speaker is playing without audio dropouts.
* **Instant Barge-In (< 20ms):** You never have to wait for Aura to finish speaking; talk mid-sentence and it immediately cuts off audio to listen.
* **Software Feedback Cancellation:** Smart filtering prevents the mic from capturing speaker playback, stopping accidental self-triggers.

### 🧠 Feature 5: Autonomous Conversational Memory Engine
* **Passive Fact Extraction:** You don't need rigid syntax. Simply say "Remember that my bike keys are in the second drawer" or "I take my medicine after dinner", and Groq's prompt architecture autonomously tags and saves the fact into persistent JSON storage.
* **Contextual Self-Reminders:** When you later ask "Where did I put my keys?" or "What do you remember about me?", it recalls the exact details instantly and answers conversationally.
* **Voice-Controlled Memory Wiping:** Easily view or purge memories with commands like "What are your memories?" or "Forget that fact".

### 🗣️ Feature 6: Dual-Tier Voice Engine (Ultra-Fast AI vs. Studio Fidelity)
* **Tier 1 (Fastest — Cartesia Sonic AI):** Our primary ultra-low latency voice engine. Generates 16kHz raw PCM audio in under 200ms, enabling our sub-second conversation response times.
* **Tier 2 (Highest Fidelity — Microsoft Cloud Neural):** Powered by Microsoft Indian Neural voices (Neerja, Swara, Aarohi, Dhwani). Slightly more latency (~600–900ms) but delivers deep emotional intonation and authentic vernacular pronunciation.
* **Persona Lock:** Voice persona locks per conversation turn so Aura never abruptly changes accents or gender mid-speech.

---

## 4. What's Next for Version 0 (ESP32-S3) 🛠️

Right now the hardware is sitting on a breadboard with jumper wires. It works like magic, but before jumping to another chip, we are turning V0 into a clean, finished desk device:

* **Custom 2-Layer PCB Design:**  
  No more loose jumper wires flying around or loose pins. We are designing a compact 60mm × 60mm 2-layer PCB. The biggest win here is separating the power traces from the INMP441 mic's analog ground plane, which kills that last bit of electrical noise and makes the audio razor-clean. Plus, everything (ESP32, MAX98357A DAC, mic) will be soldered onboard with a single USB-C port for power and flashing.

* **3D-Printed Acoustic Enclosure:**  
  A bare 3W speaker just sitting on a desk sounds tinny. Putting it into a calculated 3D-printed resonance chamber with a tiny front bass reflex port gives it actual punch and warmth. More importantly, we're adding an internal wall (acoustic baffle) between the speaker cone and the mic soundhole so the mic doesn't pick up speaker vibrations. On top, a frosted acrylic ring will diffuse the 8 LEDs into a clean, pulsing glow.

* **Local Smart Home Control (Home Assistant & Matter):**  
  Instead of relying on cloud skills, V0 will talk directly to Home Assistant over our local Wi-Fi. It will switch room lights, control fans, and toggle relays with zero internet. If the Wi-Fi drops, basic voice commands ("turn on desk light", "fan 50%") will still execute locally on the spot.

---

## 5. Next-Gen Edition: Autonomous AI Rover (Raspberry Pi 5 + Groq Cloud Brain) 🚀

Version 0 proved that we can turn bare microcontroller silicon into a full-duplex phone. For the next generation, we are mounting a Raspberry Pi 5 onto an autonomous mobile rover chassis. 

We aren't running heavy, slow local LLMs on the Pi — it connects directly to our high-speed Groq LPU pipeline over Wi-Fi (Whisper Turbo + Groq LLM) so it reasons and speaks back in under a second while moving around the room.

Here is the exact 31-feature roadmap we are building:

### 👁️ Category 1: Computer Vision & Perception
* **Autonomous "Follow-Me" Tracking:** Pi camera runs OpenCV/MediaPipe body tracking, calculating horizontal angles to roll behind you from room to room.
* **"See and Ask" Multimodal Vision:** Point the camera at any component, book, or food item; it snaps a frame, pings the vision model, and answers in under a second.
* **Touchless Hand Gesture Control:** Steer the robot with hand signs (✋ palm to brake, 👍 thumbs up to follow, ✌️ peace to snap a photo).
* **WhatsApp Photo & Video Snapper:** Say "Take a 5-second video and send it to Mom"—the Pi records and sends it directly via messaging APIs.
* **Auto Night-Vision Headlights:** Camera tracks ambient light levels and turns on high-power LEDs automatically in dark hallways or under furniture.
* **Face Recognition & Greetings:** Recognizes family members entering the room and delivers personalized morning updates or reminders.

### 🤖 Category 2: Robotics, Navigation & Autonomy
* **ArUco Marker Auto-Docking:** Spots the printed AprilTag/ArUco marker on the wall charger and aligns itself into spring-loaded charging pins.
* **Low-Battery Auto-Return:** When the battery drops below 15%, it interrupts roaming and drives back to the dock on its own.
* **Ultrasonic Crash Shield:** HC-SR04 ultrasonic array continuously sweeps for walls, pets, or table legs to hit emergency brakes in under 1ms.
* **FPV Smartphone Cockpit:** Streams low-latency WebRTC video straight to your phone browser with on-screen virtual driving joysticks.
* **Wheel Stall Self-Rescue:** Detects if wheels get stuck on a thick carpet edge or wire, automatically wiggling and reversing to free itself.
* **Gimbal Laser Pointer & Spotlight:** Pan-tilt servo rig with a mounted pointer/spotlight for pinpointing objects across the room.

### 🏠 Category 3: Smart Home & Climate Automation
* **JioFiber STB & Android TV Control:** Connects over local Wi-Fi ADB to your TV/Set-top box to launch YouTube and search shows on voice command.
* **Closed-Loop Smart AC Climate Control:** Ambient DHT sensor monitors room temperature while the gimbal IR transmitter aims at your AC to maintain target room temps.
* **Room Light & Appliance Scout:** Tell it to roll into another room to check if lights or fans were left running, and report back.
* **Universal Voice IR Blaster:** Learns and fires IR hex codes to control older TVs, soundbars, and air conditioners.
* **Morning Bedside Butler:** Wakes up on a morning timer, navigates to your bedside, and delivers your weather, schedule, and news briefing.
* **Mobile Bluetooth & Spotify Boombox:** Streams music through its onboard speaker while driving alongside you around the house.

### 🏋️ Category 4: AI Health, Fitness & Gym Coach
* **AI Push-Up & Pull-Up Counter:** MediaPipe Pose tracks elbow joint angles (flexion < 90° to extension > 160°) and calls out rep counts out loud.
* **Plank Form Corrector:** Checks spine-to-hip alignment geometry and warns you if your hips are sagging or arched too high.
* **Desk Posture Sentinel:** Checks your seating posture during study/work sessions and gives a spoken nudge if you start slouching.
* **Hydration & Stretch Butler:** Roaming timer that finds you during long desk sessions to remind you to drink water and stand up.
* **Workout Cadence DJ:** Matches workout speech cadence and speeds up audio cues when you hit your target rep pace.
* **Voice-Guided Stretching Coach:** Guides post-workout cool-downs with spoken countdown timers and joint checks.

### 🛡️ Category 5: Security, Telephony & Ambient Intelligence
* **Autonomous Night Security Patrol:** Runs scheduled night patrols through the house, recording video clips whenever motion is detected.
* **Intruder Photo Push Alert:** If an unknown face appears during sentry mode, it snaps a photo and alerts your phone instantly.
* **Hands-Free SIP Landline Calling:** Native SIP client over JioFiber IMS allowing you to place and take actual phone calls hands-free through the rover.
* **Roaming Family Voice Intercom:** Say "Tell Dad dinner is ready"—it drives to his room, detects his presence, and plays your voice memo.
* **Multilingual Vernacular Engine:** Switches naturally across Hindi, Gujarati, Marathi, and English without losing context.
* **Interactive Voice Quizzer:** Multi-turn study quiz partner for engineering concepts, tech trivia, and exams.
* **High-Speed Groq Cloud Pipeline:** Offloads all heavy reasoning to Groq LPUs over Wi-Fi (Whisper Turbo + Groq LLM) for instantaneous sub-second response times.

---

<a id="part-3-autonomous-long-term-memory-stardance-demo"></a>

## 6. Part 3: Autonomous Long-Term Memory & Stardance Identity Demo 🧠

Most DIY voice assistants suffer from instant amnesia — every query starts from scratch with zero context about who you are or what you're working on.

In this update, I gave Aura persistent conversational memory that actually remembers facts across power cycles and conversations, without relying on static, hardcoded system prompts:

### 💡 How the Live Demo Works:
1. **Natural Identity & Project Stating:**  
   I casually tell the assistant:  
   > *"I am Shravan and I have registered you on Stardance platform."*  
   Without any rigid commands or weird syntax, the backend extracts:
   * **User Name:** `Shravan`
   * **Platform Action:** `Registered on Stardance platform`
   * Writes the fact directly into persistent storage and syncs live with our local web dashboard over WebSockets in real time.

2. **Instant Conversational Recall (<600ms):**  
   Right after, I ask:  
   > *"Where did I register you?"*  
   Aura checks its persistent semantic memory slot and replies instantly:  
   > *"You registered me on Stardance platform."*

3. **Dynamic Slot Overwriting & Full User Control:**  
   If I tell it a new project name or register it somewhere else later, it intelligently overwrites the previous platform slot instead of creating conflicting notes. And if I say *"Delete all your memory"*, it wipes the slate clean instantly.

📺 **Watch the live hardware demo:** [Watch Video 3 on YouTube Shorts](https://youtu.be/rkv8eTRfRxI)



