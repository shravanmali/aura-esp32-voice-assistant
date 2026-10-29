with open(r'c:\Users\VICTUS\OneDrive\Desktop\Pappu Pelu\ESP 32\v0\voice_server.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update handle_start to disable is_listening during telephone calls unless explicit 'alexa' wake word
old_start_target = """    audio_buffer = bytearray()
    is_listening = True"""

new_start_target = """    audio_buffer = bytearray()
    if call_audio_bridge.is_active and not wake_word_phrase:
        is_listening = False
        print("[TELEPHONY ACTIVE] ESP32 Microphone dedicated to live telephone call. Assistant VAD bypassed.")
        return 0
    is_listening = True"""

# 2. Update handle_audio to return immediately during telephone calls
old_audio_target = """async def handle_audio(data: bytes, pcm_type: bytes | None = None) -> None:
    \"\"\"Receives incoming microphone frames from ESP32 with DC offset correction and multi-frame adaptive VAD.\"\"\"
    if call_audio_bridge.is_active:
        call_audio_bridge.feed_esp32_mic_audio(data)
    global audio_buffer, is_listening, speech_confirmed, speech_frames_count, silence_frames_count"""

new_audio_target = """async def handle_audio(data: bytes, pcm_type: bytes | None = None) -> None:
    \"\"\"Receives incoming microphone frames from ESP32 with DC offset correction and multi-frame adaptive VAD.\"\"\"
    if call_audio_bridge.is_active:
        call_audio_bridge.feed_esp32_mic_audio(data)
        if not is_listening:
            return
    global audio_buffer, is_listening, speech_confirmed, speech_frames_count, silence_frames_count"""

norm_text = text.replace('\r\n', '\n')
norm_old_start = old_start_target.replace('\r\n', '\n')
norm_old_audio = old_audio_target.replace('\r\n', '\n')

assert norm_old_start in norm_text, "old_start_target not found!"
norm_text = norm_text.replace(norm_old_start, new_start_target.replace('\r\n', '\n'))

assert norm_old_audio in norm_text, "old_audio_target not found!"
norm_text = norm_text.replace(norm_old_audio, new_audio_target.replace('\r\n', '\n'))

with open(r'c:\Users\VICTUS\OneDrive\Desktop\Pappu Pelu\ESP 32\v0\voice_server.py', 'w', encoding='utf-8') as f:
    f.write(norm_text)

print("SUCCESS: Patched voice_server.py with pure Telephony Full-Duplex routing & VAD isolation!")

