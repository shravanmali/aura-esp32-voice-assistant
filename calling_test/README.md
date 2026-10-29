# Wi-Fi Landline Calling Testbed (Jio AirFiber SIP)

This standalone module allows you to test outgoing **Wi-Fi Calling & Ringing** from your PC's localhost using your Home Wi-Fi line.

---

## 🚀 Quick Start

1. **Start the Calling Test Server**:
   ```bash
   cd "calling_test"
   python app.py
   ```
2. **Open in Browser**:
   Open **[http://localhost:5050](http://localhost:5050)** on your PC or phone.
3. **Ring Any Number**:
   - Enter destination mobile number (e.g. `+91 9876543210`).
   - Click **📞 RING PHONE**.
   - Watch the real-time SIP protocol signaling:
     1. `INVITE sip:+91... SIP/2.0`
     2. `100 Trying`
     3. `180 Ringing` (Destination phone alerts)
   - Hear the authentic Indian dual-tone ringback tone (400Hz + 450Hz) synthesized live through your PC speakers!
   - Click **📴 HANG UP** to stop.

---

## 🔧 Two Dialing Modes Available

1. **⚡ Interactive SIP Protocol Simulation (Default)**:
   - Accurately demonstrates carrier handshake, realistic latency (~1.0s to ring), and live Web Audio acoustic ringing tone.
2. **📡 Local SIP UDP Client**:
   - Crafts raw RFC 3261 SIP datagrams and sends UDP `INVITE` packets directly to your local gateway IP (`192.168.29.1:5060` or `192.168.31.1:5060`).

