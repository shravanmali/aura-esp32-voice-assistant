import os
import re

ini_path = os.path.join(os.path.dirname(__file__), "microsip", "microsip.ini")
with open(ini_path, "r", encoding="utf-16le") as f:
    content = f.read()

content = re.sub(r'audiooutputdevice\s*=.*', 'audiooutputdevice ="CABLE Input (VB-Audio Virtual C"', content)
content = re.sub(r'audioringdevice\s*=.*', 'audioringdevice ="CABLE Input (VB-Audio Virtual C"', content)
content = re.sub(r'audioinputdevice\s*=.*', 'audioinputdevice ="Microphone (OMEN Cam & Voice)"', content)

with open(ini_path, "w", encoding="utf-16le") as f:
    f.write(content)

print("Updated microsip.ini successfully with isolated audio channels!")

