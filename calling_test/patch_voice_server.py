with open(r'c:\Users\VICTUS\OneDrive\Desktop\Pappu Pelu\ESP 32\v0\voice_server.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_block = """def send_call_audio_to_esp32(pcm_chunk: bytes):
    global client
    if client and is_connected():
        try:
            client.send_voice_assistant_audio(pcm_chunk)
        except Exception:
            pass

def monitor_active_call_session():
    \"\"\"Watches the call state and keeps the pure ESP32 hardware audio pipeline active.\"\"\"
    global client
    print("[CALL MONITOR] Telecom session monitor started.")
    stream_opened = False
    while True:
        time.sleep(0.3)
        try:
            import requests
            r = requests.get("http://localhost:5050/api/status", timeout=1.5)
            data = r.json()
            state = data.get("state", "idle")
            if state in ("dialing", "ringing", "connected"):
                if not stream_opened and client and is_connected():
                    try:
                        # Open ESP32 MAX98357A I2S DAC for receiving telecom audio
                        client.send_voice_assistant_event(VoiceAssistantEventType.VOICE_ASSISTANT_RUN_START, None)
                        client.send_voice_assistant_event(VoiceAssistantEventType.VOICE_ASSISTANT_TTS_START, {"text": "Telecom Call"})
                        client.send_voice_assistant_event(VoiceAssistantEventType.VOICE_ASSISTANT_TTS_STREAM_START, None)
                        stream_opened = True
                        print("[CALL MONITOR] ESP32 Speaker I2S pipeline armed and open!")
                    except Exception as e:
                        print(f"[CALL MONITOR ERROR arming ESP32 speaker]: {e}")
                if not call_audio_bridge.is_active:
                    call_audio_bridge.start(send_call_audio_to_esp32)
            elif state in ("ended", "idle"):
                if call_audio_bridge.is_active:
                    call_audio_bridge.stop()
                if stream_opened and client and is_connected():
                    try:
                        client.send_voice_assistant_event(VoiceAssistantEventType.VOICE_ASSISTANT_TTS_STREAM_END, None)
                        client.send_voice_assistant_event(VoiceAssistantEventType.VOICE_ASSISTANT_RUN_END, None)
                        stream_opened = False
                        print("[CALL MONITOR] ESP32 Speaker I2S pipeline closed cleanly.")
                    except Exception as e:
                        pass
                break
        except Exception:
            pass
    print("[CALL MONITOR] Telecom session finished.")"""

new_block = """def send_call_audio_to_esp32(pcm_chunk: bytes):
    global client, loop
    if client and is_connected() and loop and not loop.is_closed():
        try:
            loop.call_soon_threadsafe(client.send_voice_assistant_audio, pcm_chunk)
        except Exception:
            pass

def monitor_active_call_session():
    \"\"\"Watches the call state and keeps the pure ESP32 hardware audio pipeline active.\"\"\"
    global client, loop, active_audio_queue
    print("[CALL MONITOR] Telecom session monitor started.")
    
    # 1. Wait until any in-progress TTS announcement finishes completely to prevent audio collision/stutter!
    while active_audio_queue is not None:
        time.sleep(0.08)
        
    stream_opened = False
    while True:
        time.sleep(0.25)
        try:
            import requests
            r = requests.get("http://localhost:5050/api/status", timeout=1.5)
            data = r.json()
            state = data.get("state", "idle")
            if state in ("dialing", "ringing", "connected"):
                if not stream_opened and client and is_connected():
                    def _arm():
                        try:
                            client.send_voice_assistant_event(VoiceAssistantEventType.VOICE_ASSISTANT_RUN_START, None)
                            client.send_voice_assistant_event(VoiceAssistantEventType.VOICE_ASSISTANT_TTS_START, {"text": "Telecom Call"})
                            client.send_voice_assistant_event(VoiceAssistantEventType.VOICE_ASSISTANT_TTS_STREAM_START, None)
                        except Exception as e:
                            print(f"[CALL MONITOR ARM ERROR]: {e}")
                    loop.call_soon_threadsafe(_arm)
                    stream_opened = True
                    print("[CALL MONITOR] ESP32 Speaker I2S pipeline armed and open!")
                    
                    # Ensure ESP32 mic is streaming frames during the call
                    try:
                        asyncio.run_coroutine_threadsafe(trigger_mic_start(), loop)
                    except Exception:
                        pass
                        
                if not call_audio_bridge.is_active:
                    call_audio_bridge.start(send_call_audio_to_esp32)
            elif state in ("ended", "idle"):
                if call_audio_bridge.is_active:
                    call_audio_bridge.stop()
                if stream_opened and client and is_connected():
                    def _disarm():
                        try:
                            client.send_voice_assistant_event(VoiceAssistantEventType.VOICE_ASSISTANT_TTS_STREAM_END, None)
                            client.send_voice_assistant_event(VoiceAssistantEventType.VOICE_ASSISTANT_RUN_END, None)
                        except Exception:
                            pass
                    loop.call_soon_threadsafe(_disarm)
                    stream_opened = False
                    print("[CALL MONITOR] ESP32 Speaker I2S pipeline closed cleanly.")
                break
        except Exception:
            pass
    print("[CALL MONITOR] Telecom session finished.")"""

norm_text = text.replace('\r\n', '\n')
norm_old = old_block.replace('\r\n', '\n')
if norm_old in norm_text:
    norm_text = norm_text.replace(norm_old, new_block.replace('\r\n', '\n'))
    with open(r'c:\Users\VICTUS\OneDrive\Desktop\Pappu Pelu\ESP 32\v0\voice_server.py', 'w', encoding='utf-8') as f:
        f.write(norm_text)
    print("SUCCESS: voice_server.py patched with thread-safe queue & collision-free TTS playback!")
else:
    print("FAILED: old_block not found in voice_server.py")
