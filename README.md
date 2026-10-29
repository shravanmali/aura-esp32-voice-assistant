# Aura ESP32-S3 Voice Assistant & Telephony Bridge (v0)

Aura is a sub-second, multi-lingual smart voice assistant and VoIP telephony bridge built on the **ESP32-S3** microcontroller, featuring on-device wake-word detection, real-time Acoustic Echo Suppression (AES), Groq-powered STT & LLM reasoning, Microsoft Neural / Cartesia TTS, and an 8-bit WS2812 RGB LED status strip.

---

## 🌟 Key Highlights

- **⚡ Sub-Second Voice Latency (<800ms End-to-End)**: Powered by Groq's high-speed LPU infrastructure (`qwen/qwen3.8-27b` and `whisper-large-v3-turbo`).
- **🎛️ Dual-Core Hardware Architecture**: ESP32-S3 running ESP-IDF 5.5.5 with Octal PSRAM at 240 MHz for high-fidelity 16 kHz I2S full-duplex audio.
- **🛡️ Acoustic Echo Suppression (AES)**: Real-time 550ms hardware latency hangover window that dynamically mutes the microphone while the speaker plays caller audio, preventing feedback loops.
- **📞 Landline Telephony Bridge (VoIP SIP)**: Native SIP landline calling over JioFiber IMS using MicroSIP, enabling voice commands like *"Alexa, call Mom"* or *"Alexa, call myself"*.
- **🌈 Aura 8-Bit WS2812 Visual Feedback Engine**: Real-time responsive RGB LED light effects driven by ESP32 RMT hardware.

---

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

