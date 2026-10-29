# Timer, Stopwatch & Smart Cooking Voice Assistant Blueprint (v0 Milestone)

## 1. System Overview & Workspace Context
- **ESP32 IP**: `192.168.31.200:6053` (ESPHome native API, micro_wake_word, I2S INMP441 mic, MAX98357A speaker).
- **Brain Server**: `voice_server.py` running on PC (`192.168.31.72:8080`).
- **Core Goal**: Perfect the local voice assistant with smart Timers, Stopwatches, and Alarms, including proactive culinary contextual intelligence, before proceeding to calling/gimbal migration.
- **Rule**: Do NOT mark Version 0 (v0) as completed until all features here are fully implemented and verified.
- **Mandatory Notification**: NTFY command must run on task completion.

---

## 2. Feature Specifications

### A. Proactive Cooking Timers & Intent Recognition
1. **Contextual Suggestion**:
   - When the user mentions cooking, boiling, or preparing food (e.g., *"Main Maggi bana raha hoon"*, *"Making tea"*, *"Boiling eggs"*, *"Heating milk"*):
   - The assistant asks proactively: *"Should I set a 2-minute timer for your Maggi?"* (or in Hindi: *"Kya main aapki Maggi ke liye 2 minute ka timer laga doon?"*).
   - If the user responds *"Yes"* / *"Haan"* / *"Sure"*, it initiates the timer immediately.
2. **Contextual Completion Alert**:
   - When the timer expires, the assistant does NOT just beep.
   - It plays a notification chime followed by a smart contextual voice alert:
     > *"Shravan, 2 minutes timer has been done for your Maggi! Look at your Maggi, is it cooked?"*
     > (or Hindi: *"Shravan, aapki Maggi ka 2 minute ka timer poora ho gaya hai! Dekhiye aapki Maggi ban gayi kya?"*).

### B. Multi-Timer Management
- **Multiple Simultaneous Timers**: E.g., a 2-minute Maggi timer and a 5-minute Tea timer running concurrently.
- **Status Queries**:
  - *"How much time is left on Maggi?"* -> *"1 minute and 15 seconds remaining for your Maggi timer."*
  - *"How many timers are running?"* -> Lists all active timers with remaining minutes/seconds.
- **Targeted Cancellation**:
  - *"Cancel Maggi timer"* -> Cancels only the Maggi timer while leaving others running.
  - *"Cancel all timers"* -> Clears all active timers.

### C. Stopwatch Features
- **Intents**:
  - *"Start stopwatch"* / *"Stopwatch shuru karo"* -> Starts background counting.
  - *"Lap stopwatch"* / *"Lap"* -> Records timestamp without stopping.
  - *"How much time on stopwatch?"* -> Returns current elapsed time.
  - *"Stop stopwatch"* / *"Reset stopwatch"* -> Reports total elapsed time and resets.

### D. Alarm Features
- **Intents**:
  - *"Set alarm for 6:30 AM"* / *"Subah 7 baje ka alarm lagao"*.
  - Recurring vs one-shot alarm scheduling.
  - Dedicated alarm tone / wake audio sequence.

### E. Web Dashboard (`http://localhost:8080`)
- Live reactive card displaying:
  - Active Timers with real-time countdown progress bars and labels.
  - Active Stopwatch with elapsed time counter and lap history.
  - Scheduled Alarms.
  - Quick action buttons (Add, Pause, Delete).

---

## 3. Data Structures for `voice_server.py`

```python
active_timers = {
    "timer_id": {
        "name": "Maggi",
        "duration": 120,
        "start_time": 1729600000.0,
        "end_time": 1729600120.0,
        "context": "cooking",
        "completion_phrase": "2 minutes timer has been done for your Maggi. Look at your Maggi, is it cooked?",
        "lang": "en",
        "task": asyncio_task_handle
    }
}

active_stopwatch = {
    "running": False,
    "start_time": None,
    "elapsed_before_pause": 0.0,
    "laps": []
}

active_alarms = [
    {
        "id": "alarm_1",
        "time_str": "06:30",
        "label": "Morning wake-up",
        "target_ts": 1729645800.0
    }
]
```

---

## 4. LLM System Prompt & Tagging Convention

The system prompt in `voice_server.py` will handle structured intent tags:
- `[TIMER_SET: <seconds> | <name> | <completion_message>]`
- `[TIMER_PROMPT: <seconds> | <dish> | <confirmation_question>]`
- `[TIMER_QUERY: <name_or_all>]`
- `[TIMER_CANCEL: <name_or_all>]`
- `[STOPWATCH: START|STOP|LAP|RESET|QUERY]`
- `[ALARM_SET: <HH:MM> | <label>]`
- `[ALARM_CANCEL: <label_or_all>]`

---

## 5. Implementation Roadmap for New Conversation
1. **Step 1**: Add robust Timer, Stopwatch, and Alarm state managers and background asyncio monitors in `voice_server.py`.
2. **Step 2**: Enhance LLM prompt with proactive cooking triggers (Maggi, tea, eggs, noodles, etc.) and tags.
3. **Step 3**: Integrate contextual TTS generation for timer expirations with audible chime.
4. **Step 4**: Update Web UI on `http://localhost:8080` with live visual cards.
5. **Step 5**: End-to-end testing with audio playback and mic queries.

