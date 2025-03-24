# pip install mss
import mss
with mss.mss() as sct:
    screen = sct.shot(output="screenshot.png")