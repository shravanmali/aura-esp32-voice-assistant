with open(r'c:\Users\VICTUS\OneDrive\Desktop\Pappu Pelu\ESP 32\v0\voice_server.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_func = """async def handle_audio(data: bytes, pcm_type: bytes | None = None) -> None:
    \"\"\"Receives incoming microphone frames from ESP32 with DC offset correction and multi-frame adaptive VAD.\"\"\"
    if call_audio_bridge.is_active:
        call_audio_bridge.feed_esp32_mic_audio(data)
        if not is_listening:
            return
    global audio_buffer, is_listening, speech_confirmed, speech_frames_count, silence_frames_count
    global ambient_noise_samples, ambient_noise_baseline, total_voiced_frames
    if not is_listening:
        return"""

new_func = """async def handle_audio(data: bytes, pcm_type: bytes | None = None) -> None:
    \"\"\"Receives incoming microphone frames from ESP32 with DC offset correction and multi-frame adaptive VAD.\"\"\"
    global audio_buffer, is_listening, speech_confirmed, speech_frames_count, silence_frames_count
    global ambient_noise_samples, ambient_noise_baseline, total_voiced_frames

    if call_audio_bridge.is_active:
        call_audio_bridge.feed_esp32_mic_audio(data)
        if not is_listening:
            return

    if not is_listening:
        return"""

norm_text = text.replace('\r\n', '\n')
norm_old = old_func.replace('\r\n', '\n')
assert norm_old in norm_text, "old_func not found!"
norm_text = norm_text.replace(norm_old, new_func.replace('\r\n', '\n'))

with open(r'c:\Users\VICTUS\OneDrive\Desktop\Pappu Pelu\ESP 32\v0\voice_server.py', 'w', encoding='utf-8') as f:
    f.write(norm_text)

print("SUCCESS: Fixed global is_listening declaration!")

