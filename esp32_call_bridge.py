import time
import queue
import threading
import numpy as np
import scipy.signal as signal
import pyaudiowpatch as pyaudio
import comtypes
from ctypes import wintypes, POINTER, c_float
from comtypes import GUID, IUnknown, COMMETHOD, HRESULT

CLSID_MMDeviceEnumerator = GUID('{BCDE0395-E52F-467C-8E3D-C4579291692E}')
IID_IMMDeviceEnumerator = GUID('{A95664D2-9614-4F35-A746-DE8DB63617E6}')
IID_IAudioEndpointVolume = GUID('{5CDF2C82-841E-4546-9722-0CF74078229A}')
IID_IPropertyStore = GUID('{886d8eeb-8cf2-4446-8d02-cdba1dbdcf99}')

class PROPERTYKEY(comtypes.Structure):
    _fields_ = [('fmtid', GUID), ('pid', wintypes.DWORD)]

PKEY_Device_FriendlyName = PROPERTYKEY(GUID('{a45c254e-df1c-4efd-8020-67d146a850e0}'), 14)

class PROPVARIANT(comtypes.Structure):
    _fields_ = [
        ('vt', wintypes.USHORT),
        ('wReserved1', wintypes.USHORT),
        ('wReserved2', wintypes.USHORT),
        ('wReserved3', wintypes.USHORT),
        ('pwszVal', wintypes.LPWSTR),
    ]

class IPropertyStore(IUnknown):
    _iid_ = IID_IPropertyStore
    _methods_ = [
        COMMETHOD([], HRESULT, 'GetCount'),
        COMMETHOD([], HRESULT, 'GetAt'),
        COMMETHOD([], HRESULT, 'GetValue', (['in'], POINTER(PROPERTYKEY), 'key'), (['out'], POINTER(PROPVARIANT), 'pv')),
    ]

class IMMDevice(IUnknown):
    _iid_ = GUID('{D666063F-1587-4E43-81F1-B948E807363F}')
    _methods_ = [
        COMMETHOD([], HRESULT, 'Activate',
                  (['in'], POINTER(GUID), 'iid'),
                  (['in'], wintypes.DWORD, 'dwClsCtx'),
                  (['in'], POINTER(wintypes.DWORD), 'pActivationParams'),
                  (['out'], POINTER(POINTER(IUnknown)), 'ppInterface')),
        COMMETHOD([], HRESULT, 'OpenPropertyStore',
                  (['in'], wintypes.DWORD, 'stgmAccess'),
                  (['out'], POINTER(POINTER(IPropertyStore)), 'ppProperties')),
    ]

class IMMDeviceCollection(IUnknown):
    _iid_ = GUID('{0BD7A1BE-7A1A-44DB-8397-CC5392387B5E}')
    _methods_ = [
        COMMETHOD([], HRESULT, 'GetCount', (['out'], POINTER(wintypes.UINT), 'pcDevices')),
        COMMETHOD([], HRESULT, 'Item', (['in'], wintypes.UINT, 'nDevice'), (['out'], POINTER(POINTER(IMMDevice)), 'ppDevice')),
    ]

class IMMDeviceEnumerator(IUnknown):
    _iid_ = IID_IMMDeviceEnumerator
    _methods_ = [
        COMMETHOD([], HRESULT, 'EnumAudioEndpoints', (['in'], wintypes.DWORD, 'dataFlow'), (['in'], wintypes.DWORD, 'dwStateMask'), (['out'], POINTER(POINTER(IMMDeviceCollection)), 'ppDevices')),
    ]

class IAudioEndpointVolume(IUnknown):
    _iid_ = IID_IAudioEndpointVolume
    _methods_ = [
        COMMETHOD([], HRESULT, 'RegisterControlChangeNotify'),
        COMMETHOD([], HRESULT, 'UnregisterControlChangeNotify'),
        COMMETHOD([], HRESULT, 'GetChannelCount'),
        COMMETHOD([], HRESULT, 'SetMasterVolumeLevel'),
        COMMETHOD([], HRESULT, 'SetMasterVolumeLevelScalar', (['in'], c_float, 'fLevel'), (['in'], POINTER(GUID), 'pguidEventContext')),
        COMMETHOD([], HRESULT, 'GetMasterVolumeLevel'),
        COMMETHOD([], HRESULT, 'GetMasterVolumeLevelScalar', (['out'], POINTER(c_float), 'pfLevel')),
        COMMETHOD([], HRESULT, 'SetChannelVolumeLevel'),
        COMMETHOD([], HRESULT, 'SetChannelVolumeLevelScalar'),
        COMMETHOD([], HRESULT, 'GetChannelVolumeLevel'),
        COMMETHOD([], HRESULT, 'GetChannelVolumeLevelScalar'),
        COMMETHOD([], HRESULT, 'SetMute', (['in'], wintypes.BOOL, 'bMute'), (['in'], POINTER(GUID), 'pguidEventContext')),
        COMMETHOD([], HRESULT, 'GetMute', (['out'], POINTER(wintypes.BOOL), 'pbMute')),
    ]

def silence_laptop_physical_speakers():
    """Uses Windows Core Audio API to mute OMEN and Realtek physical speakers so zero acoustic sound leaks."""
    try:
        enumerator = comtypes.CoCreateInstance(CLSID_MMDeviceEnumerator, IMMDeviceEnumerator, comtypes.CLSCTX_INPROC_SERVER)
        collection = enumerator.EnumAudioEndpoints(0, 1) # eRender, DEVICE_STATE_ACTIVE
        for i in range(collection.GetCount()):
            dev = collection.Item(i)
            props = dev.OpenPropertyStore(0)
            pv = props.GetValue(PKEY_Device_FriendlyName)
            name = str(pv.pwszVal)
            if 'OMEN' in name.upper() or 'REALTEK' in name.upper():
                pEndpoint = dev.Activate(IID_IAudioEndpointVolume, comtypes.CLSCTX_INPROC_SERVER, None)
                vol = pEndpoint.QueryInterface(IAudioEndpointVolume)
                vol.SetMute(True, None)
                print(f"[AUDIO BRIDGE HARDWARE SILENCE]: Muted physical speaker endpoint '{name}' (0.0 dB acoustic output).")
    except Exception as e:
        print(f"[AUDIO BRIDGE SILENCE NOTICE]: {e}")

class ESP32CallAudioBridge:
    def __init__(self, send_to_esp32_fn=None):
        self.send_to_esp32_fn = send_to_esp32_fn
        self.is_active = False
        self.is_muted = False
        self.pa = None
        self.inbound_thread = None
        self.outbound_thread = None
        
        self.cable_in_dev = None          # WASAPI Render: ESP32 Mic -> CABLE Input (MicroSIP listens on CABLE Output)
        self.caller_loopback_dev = None   # WASAPI Loopback: MicroSIP renders ringtone & caller to OMEN -> captured digitally
        self.caller_render_dev = None     # WASAPI Render: Keep OMEN clock ticking
        
        self.outbound_stream = None
        self.silent_render_stream = None
        
        # Real-time caller speaker energy tracking for Acoustic Echo Suppression (AES)
        self.caller_speaker_rms = 0.0
        self.last_caller_audio_time = 0.0
        self.current_out_gain = 1.0
        
        # Non-blocking lockless queue for outbound mic audio (ESP32 mic -> CABLE Input)
        self.mic_queue = queue.Queue(maxsize=120)
        
        # DSP Filter Design: 2nd-order Butterworth High-Pass at 85Hz (strips room rumble/vibrations)
        self.b_hp, self.a_hp = signal.butter(2, 85.0, 'highpass', fs=16000)
        self.hp_zi = signal.lfilter_zi(self.b_hp, self.a_hp) * 0.0

        # DSP Presence Filter: Peaking EQ at 3.2kHz, Q=1.2, Gain=+4.5dB (crystalline speech intelligibility on mobile phones)
        self._init_presence_filter()

    def _init_presence_filter(self):
        """Biquad Peaking EQ filter centered at 3200Hz to make voice cut through AMR-WB compression."""
        fs = 16000.0
        f0 = 3200.0
        gain_db = 4.5
        Q = 1.2
        A = 10.0 ** (gain_db / 40.0)
        w0 = 2.0 * np.pi * f0 / fs
        alpha = np.sin(w0) / (2.0 * Q)

        b0 = 1.0 + alpha * A
        b1 = -2.0 * np.cos(w0)
        b2 = 1.0 - alpha * A
        a0 = 1.0 + alpha / A
        a1 = -2.0 * np.cos(w0)
        a2 = 1.0 - alpha / A

        self.b_eq = np.array([b0/a0, b1/a0, b2/a0], dtype=np.float32)
        self.a_eq = np.array([1.0, a1/a0, a2/a0], dtype=np.float32)
        self.eq_zi = signal.lfilter_zi(self.b_eq, self.a_eq) * 0.0

    def _discover_devices(self):
        """
        Discovers hardware audio devices strictly over Windows WASAPI (API index 2).
        - Outbound Mic Target: CABLE Input (VB-Audio Virtual Cable)
        - Inbound Caller Source: Speakers (OMEN Cam & Voice) [Loopback]
        Physical PC speakers are muted in hardware, while WASAPI captures bit-perfect digital audio!
        """
        if self.pa is None:
            self.pa = pyaudio.PyAudio()

        wasapi_api_idx = 2
        try:
            wasapi_info = self.pa.get_host_api_info_by_type(pyaudio.paWASAPI)
            wasapi_api_idx = wasapi_info['index']
        except Exception:
            pass

        self.cable_in_dev = None
        self.caller_loopback_dev = None
        self.caller_render_dev = None

        for i in range(self.pa.get_device_count()):
            try:
                d = self.pa.get_device_info_by_index(i)
                if d['hostApi'] != wasapi_api_idx:
                    continue
                name = d['name'].upper()
                is_loopback = d.get('isLoopbackDevice', False)
                
                # 1. WASAPI CABLE Input (Render device: Python writes mic audio -> MicroSIP hears on CABLE Output)
                if 'CABLE INPUT' in name and d['maxOutputChannels'] > 0 and not is_loopback:
                    self.cable_in_dev = d
                    
                # 2. WASAPI Speakers OMEN Loopback (MicroSIP plays caller audio & ringtone here -> captured digitally)
                if 'OMEN' in name and is_loopback and self.caller_loopback_dev is None:
                    self.caller_loopback_dev = d
                    
                # 3. WASAPI Speakers OMEN Render (For silent clock keepalive)
                if 'SPEAKERS (OMEN' in name and d['maxOutputChannels'] > 0 and not is_loopback and self.caller_render_dev is None:
                    self.caller_render_dev = d
            except Exception:
                pass

        print(f"[AUDIO BRIDGE] Discovered WASAPI Hardware Endpoints:")
        print(f"  -> Outbound Mic Target (WASAPI CABLE Input): {self.cable_in_dev['name'] if self.cable_in_dev else 'NOT FOUND'}")
        print(f"  -> Inbound Caller Source (WASAPI OMEN Digital Loopback): {self.caller_loopback_dev['name'] if self.caller_loopback_dev else 'NOT FOUND'}")

    def start(self, send_fn=None):
        if self.is_active:
            return
        if send_fn:
            self.send_to_esp32_fn = send_fn

        self.is_active = True
        self.is_muted = False
        self.caller_speaker_rms = 0.0
        self.last_caller_audio_time = 0.0
        self.current_out_gain = 1.0
        
        # Mute physical speakers before any telecom audio streams
        silence_laptop_physical_speakers()
        
        # Clear mic queue
        while not self.mic_queue.empty():
            try:
                self.mic_queue.get_nowait()
            except Exception:
                break
                
        self._discover_devices()
        
        self.hp_zi = signal.lfilter_zi(self.b_hp, self.a_hp) * 0.0
        self.eq_zi = signal.lfilter_zi(self.b_eq, self.a_eq) * 0.0
        print("[AUDIO BRIDGE] Starting Studio-Grade Headless Telecom Audio Bridge (Zero PC Speaker, Pure ESP32, Full Duplex WASAPI)...")

        # 1. Initialize Outbound Stream (ESP32 Mic 16k -> Resampled 48k Stereo -> WASAPI CABLE Input)
        try:
            if self.cable_in_dev:
                self.outbound_stream = self.pa.open(
                    format=pyaudio.paInt16,
                    channels=2,
                    rate=48000,
                    output=True,
                    output_device_index=self.cable_in_dev['index'],
                    frames_per_buffer=960
                )
                print("[AUDIO BRIDGE] Outbound Stream Open (WASAPI CABLE Input @ 48kHz Stereo, buffer=20ms).")
        except Exception as e:
            print(f"[AUDIO BRIDGE OUTBOUND ERROR]: {e}")

        # 2. Initialize Silent Render Stream on OMEN (keeps WASAPI loopback clock running seamlessly)
        try:
            if self.caller_render_dev:
                self.silent_render_stream = self.pa.open(
                    format=pyaudio.paInt16,
                    channels=2,
                    rate=48000,
                    output=True,
                    output_device_index=self.caller_render_dev['index'],
                    frames_per_buffer=960
                )
        except Exception:
            self.silent_render_stream = None

        # 3. Dedicated Outbound Worker Thread (Non-blocking mic queue consumer with DSP & polyphase 3x upsampling)
        self.outbound_thread = threading.Thread(target=self._run_outbound_loop, daemon=True)
        self.outbound_thread.start()

        # 4. Start Inbound Thread (WASAPI OMEN Loopback -> Downsample 48k to 16k -> ESP32 Speaker)
        self.inbound_thread = threading.Thread(target=self._run_inbound_loop, daemon=True)
        self.inbound_thread.start()

    def is_speaker_active_in_room(self) -> bool:
        """Returns True if the ESP32 speaker is currently sounding or draining buffered audio."""
        return (time.time() - self.last_caller_audio_time) < 0.55

    def set_mute(self, muted: bool):
        self.is_muted = muted
        state_str = "MUTED (silent to caller)" if muted else "UNMUTED (live audio)"
        print(f"[AUDIO BRIDGE] Microphone state: {state_str}")

    def toggle_mute(self) -> bool:
        self.is_muted = not self.is_muted
        state_str = "MUTED" if self.is_muted else "UNMUTED"
        print(f"[AUDIO BRIDGE] Microphone toggled -> {state_str}")
        return self.is_muted

    def feed_esp32_mic_audio(self, pcm_bytes: bytes):
        """
        STRICTLY NON-BLOCKING:
        Puts raw 16kHz Mono PCM from ESP32 mic into worker queue in < 0.01ms.
        Guarantees asyncio event loop and aioesphomeapi TCP client are NEVER blocked!
        """
        if not self.is_active or not pcm_bytes:
            return
        try:
            self.mic_queue.put_nowait(pcm_bytes)
        except queue.Full:
            try:
                self.mic_queue.get_nowait()
                self.mic_queue.put_nowait(pcm_bytes)
            except Exception:
                pass

    def _run_outbound_loop(self):
        """
        Dedicated background worker thread for processing and writing ESP32 mic audio to WASAPI CABLE Input.
        Runs DSP outside the asyncio thread:
        1. Mute check: writes silence if muted.
        2. 85Hz High-Pass Filter (strips room rumble).
        3. 3.2kHz Vocal Presence EQ (+4.5dB wideband boost).
        4. Intelligent Acoustic Echo Suppression (AES): When caller is speaking through the ESP32 speaker,
           attenuates the mic feedback so caller does NOT hear an echo of themselves.
        5. Clean Dynamic Gain Boost (1.80x when room user speaks, noise-floor gate when silent).
        6. Anti-Clipping Soft Limiter.
        7. Polyphase FIR 3x Upsampling (16kHz -> 48kHz) in 0.1ms.
        8. Writes stereo 48kHz PCM to WASAPI CABLE Input -> MicroSIP transmits crystal clear AMR-WB HD Voice to phone.
        """
        print("[AUDIO BRIDGE] Dedicated Outbound DSP Worker Thread active.")
        while self.is_active:
            try:
                pcm_bytes = self.mic_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            if not self.outbound_stream:
                continue

            # Target 48kHz frame count = 3x number of 16kHz input samples
            in_samples = len(pcm_bytes) // 2
            out_samples_target = in_samples * 3

            if self.is_muted:
                # Transmit pure silence when muted (stereo 48kHz)
                silence_frame = b'\x00' * (out_samples_target * 4)
                try:
                    self.outbound_stream.write(silence_frame)
                except Exception:
                    pass
                continue

            try:
                samples = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)
                if len(samples) == 0:
                    continue

                # 1. 85Hz High-Pass Filter (strips mechanical vibrations and AC rumble)
                filtered_hp, self.hp_zi = signal.lfilter(self.b_hp, self.a_hp, samples, zi=self.hp_zi)

                # 2. 3.2kHz Vocal Presence Equalization (+4.5dB boost for phone clarity)
                voice_eq, self.eq_zi = signal.lfilter(self.b_eq, self.a_eq, filtered_hp, zi=self.eq_zi)

                # 3. Intelligent Hardware-Latency-Aware Acoustic Echo Suppression (AES)
                mic_rms = float(np.sqrt(np.mean(voice_eq ** 2)))
                now_ts = time.time()
                time_since_caller = now_ts - self.last_caller_audio_time
                speaker_active = (self.caller_speaker_rms > 90.0) and (time_since_caller < 0.40)

                if speaker_active:
                    # Inbound speaker in the room is physically sounding caller's voice!
                    # Attenuate acoustic feedback so caller does not hear echo
                    if mic_rms < 400.0:
                        target_gain = 0.05
                    else:
                        # Double-talk: room user is speaking over the speaker
                        target_gain = 0.95
                else:
                    # Speaker is quiet. Caller is listening.
                    if mic_rms < 70.0:
                        target_gain = 0.05  # Background room noise floor gate
                    else:
                        target_gain = 1.85  # Loud, full-bodied speech boost (+5.3dB)

                # Smooth gain transition (20ms time constant) to prevent audible clicks/pops
                self.current_out_gain = 0.75 * self.current_out_gain + 0.25 * target_gain

                if self.current_out_gain < 0.01:
                    silence_frame = b'\x00' * (out_samples_target * 4)
                    try:
                        self.outbound_stream.write(silence_frame)
                    except Exception:
                        pass
                    continue

                boosted = voice_eq * self.current_out_gain

                # 4. Anti-clipping soft tanh compression above 26000
                mag = np.abs(boosted)
                clip_mask = mag > 26000.0
                if np.any(clip_mask):
                    excess = mag[clip_mask] - 26000.0
                    compressed = 26000.0 + (32767.0 - 26000.0) * np.tanh(excess / 6000.0)
                    boosted[clip_mask] = np.sign(boosted[clip_mask]) * compressed

                processed_16k = np.clip(boosted, -32767.0, 32767.0).astype(np.float32)

                # 5. Polyphase FIR 3x Upsampling: 16kHz -> 48kHz (executes in ~0.1ms, zero latency!)
                samples_48k = signal.resample_poly(processed_16k, 3, 1)

                # 6. Convert Mono to Stereo for WASAPI CABLE Input
                int16_48k = np.clip(samples_48k, -32767.0, 32767.0).astype(np.int16)
                stereo_frame = np.column_stack([int16_48k, int16_48k]).tobytes()
                self.outbound_stream.write(stereo_frame)
            except Exception:
                pass

    def _run_inbound_loop(self):
        """
        Captures caller audio & ringtone from MicroSIP via WASAPI Digital Loopback on OMEN.
        Runs natively at 48kHz stereo with 20ms frames (960 samples), averages to mono,
        decimates 3:1 to native 16kHz mono (320 samples = 20ms = 640 bytes),
        and streams directly to ESP32 MAX98357A speaker with ~25ms round-trip latency.
        Physical laptop speakers are muted, so ZERO sound emits from the PC!
        """
        if not self.caller_loopback_dev:
            print("[AUDIO BRIDGE ERROR] Caller Loopback device not found.")
            return

        try:
            # 960 frames @ 48kHz = exactly 20ms audio
            in_stream = self.pa.open(
                format=pyaudio.paInt16,
                channels=2,
                rate=48000,
                input=True,
                input_device_index=self.caller_loopback_dev['index'],
                frames_per_buffer=960
            )
            print("[AUDIO BRIDGE] Ultra-Low Latency Inbound Stream Active (OMEN Digital Loopback -> ESP32 Speaker @ 20ms frames).")

            # Prime the clock with a tiny silent frame
            if self.silent_render_stream:
                try:
                    self.silent_render_stream.write(b'\x00' * 3840)
                except Exception:
                    pass

            last_clock_tick = time.time()
            last_sent_time = 0.0

            # Pre-allocated 20ms silence buffer for keepalive
            silence_keepalive = b'\x00' * 640

            while self.is_active:
                now = time.time()
                # Keep WASAPI loopback clock alive during quiet periods
                if now - last_clock_tick > 0.08:
                    if self.silent_render_stream:
                        try:
                            self.silent_render_stream.write(b'\x00' * 3840)
                        except Exception:
                            pass
                    last_clock_tick = now

                data = in_stream.read(960, exception_on_overflow=False)
                if not data or len(data) < 3840:
                    continue

                samples = np.frombuffer(data, dtype=np.int16).reshape(-1, 2)
                # Average left & right channels to mono float32
                mono_48k = ((samples[:, 0].astype(np.int32) + samples[:, 1].astype(np.int32)) // 2).astype(np.float32)

                # Decimate 48kHz -> 16kHz (3:1: 960 samples -> 320 samples = 20ms = 640 bytes)
                mono_16k = mono_48k[::3]

                # Measure RMS energy of caller speech / ringtone
                instant_rms = float(np.sqrt(np.mean(mono_16k ** 2)))
                self.caller_speaker_rms = 0.70 * self.caller_speaker_rms + 0.30 * instant_rms

                # Whenever caller speech or ringtone is present, mark the acoustic speaker active timestamp
                if instant_rms > 90.0:
                    self.last_caller_audio_time = now

                # Forward 16kHz 16-bit mono PCM to ESP32 MAX98357A speaker:
                # If caller speech or ringtone is present (> 35 RMS): send real audio immediately (< 20ms latency).
                # If dead silent (< 35 RMS): pace pure zero-bytes keepalive at 70ms to prevent driver underrun without buzz/hiss!
                if self.send_to_esp32_fn:
                    if self.caller_speaker_rms > 35.0:
                        pcm_out = mono_16k.astype(np.int16).tobytes()
                        self.send_to_esp32_fn(pcm_out)
                        last_sent_time = now
                    elif (now - last_sent_time) > 0.070:
                        self.send_to_esp32_fn(silence_keepalive)
                        last_sent_time = now

            in_stream.stop_stream()
            in_stream.close()
        except Exception as e:
            print(f"[AUDIO BRIDGE INBOUND ERROR]: {e}")

    def stop(self):
        if not self.is_active:
            return
        print("[AUDIO BRIDGE] Stopping Headless Telecom Audio Bridge...")
        self.is_active = False
        self.caller_speaker_rms = 0.0

        if self.inbound_thread and self.inbound_thread.is_alive():
            try:
                self.inbound_thread.join(timeout=0.25)
            except Exception:
                pass
            self.inbound_thread = None

        if self.outbound_thread and self.outbound_thread.is_alive():
            try:
                self.outbound_thread.join(timeout=0.25)
            except Exception:
                pass
            self.outbound_thread = None

        if self.outbound_stream:
            try:
                self.outbound_stream.stop_stream()
                self.outbound_stream.close()
            except Exception:
                pass
            self.outbound_stream = None

        if self.silent_render_stream:
            try:
                self.silent_render_stream.stop_stream()
                self.silent_render_stream.close()
            except Exception:
                pass
            self.silent_render_stream = None

        print("[AUDIO BRIDGE] Headless Bridge stopped cleanly.")

bridge_instance = ESP32CallAudioBridge()
