import subprocess
import sys

from hba.ports import Box


def test_ports_import_without_hardware_libraries():
    code = (
        "import sys, hba.ports;"
        "bad = [m for m in ('cv2','torch','serial','ultralytics','numpy') if m in sys.modules];"
        "print(','.join(bad))"
    )
    out = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True, check=True)
    assert out.stdout.strip() == ""


def test_box_geometry():
    box = Box(x1=100, y1=250, x2=180, y2=300, cls=1, conf=0.9)
    assert box.width == 80
    assert box.top == 250
