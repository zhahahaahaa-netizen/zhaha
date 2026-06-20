import tkinter as tk
from PIL import Image, ImageTk
import pystray
from pystray import MenuItem as item
import winsound
import threading
import random
import time
import json
import os
import sys
import winreg
import subprocess

# ---------------- APP INFO ----------------

APP_NAME = "Jumpscare"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

APP_DATA_DIR = os.path.join(
    os.path.expanduser("~"),
    "AppData",
    "Roaming",
    APP_NAME
)
os.makedirs(APP_DATA_DIR, exist_ok=True)

SETTINGS_FILE = os.path.join(APP_DATA_DIR, "settings.json")

# ---------------- SETTINGS FUNCTION (MUST BE FIRST) ----------------

def sync_push_to_0g():
    sidecar_dir = os.path.join(BASE_DIR, "sidecar")
    settings_copy = os.path.join(sidecar_dir, "settings.json")

    try:
        with open(settings_copy, "w") as f:
            json.dump(settings, f, indent=4)

        result = subprocess.run(
            ["node", "sync.js", "push", "settings.json"],
            cwd=sidecar_dir,
            timeout=60,
            capture_output=True,
            text=True,
        )
        print("0G PUSH STDOUT:", result.stdout)
        print("0G PUSH STDERR:", result.stderr)
        print("0G PUSH RETURN CODE:", result.returncode)
    except Exception as e:
        print("0G push failed (app continues normally):", e)

def save_settings():
    try:
        print("Saving settings...")  # DEBUG
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print("SAVE ERROR:", e)

    threading.Thread(target=sync_push_to_0g, daemon=True).start()

# ---------------- RESOURCE PATH ----------------

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = BASE_DIR
    return os.path.join(base_path, relative_path)

def get_exe_path():
    if getattr(sys, 'frozen', False):
        return sys.executable
    return os.path.abspath(__file__)

# ---------------- SETTINGS ----------------

TIME_RANGES = {
    "10-30 min": (10, 30),
    "30-60 min": (30, 60),
    "1-2 hours": (60, 120),
}

settings = {
    "enabled": True,
    "range": "10-30 min",
    "startup": True
}


# ALWAYS FORCE CREATE FILE
save_settings()

# ---------------- STARTUP (REGISTRY) ----------------

def set_startup(enable: bool):
    key = r"Software\Microsoft\Windows\CurrentVersion\Run"

    try:
        if enable:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                key,
                0,
                winreg.KEY_SET_VALUE
            ) as reg:
                winreg.SetValueEx(
                    reg,
                    APP_NAME,
                    0,
                    winreg.REG_SZ,
                    get_exe_path()
                )
        else:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                key,
                0,
                winreg.KEY_SET_VALUE
            ) as reg:
                try:
                    winreg.DeleteValue(reg, APP_NAME)
                except:
                    pass
    except Exception as e:
        with open(os.path.join(APP_DATA_DIR, "startup_error.txt"), "w") as f:
            f.write(str(e))

def is_startup_enabled():
    key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_READ) as reg:
            winreg.QueryValueEx(reg, APP_NAME)
            return True
    except:
        return False

settings["startup"] = is_startup_enabled()

# ---------------- MEDIA ----------------

IMAGE_FOLDER = resource_path("images")
SOUND_FOLDER = resource_path("sounds")

def get_images():
    if not os.path.isdir(IMAGE_FOLDER):
        return []
    return [
        os.path.join(IMAGE_FOLDER, f)
        for f in os.listdir(IMAGE_FOLDER)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

def get_sounds():
    if not os.path.isdir(SOUND_FOLDER):
        return []
    return [
        os.path.join(SOUND_FOLDER, f)
        for f in os.listdir(SOUND_FOLDER)
        if f.lower().endswith(".wav")
    ]

# ---------------- JUMPSCARE ----------------

def show_jumpscare():
    images = get_images()
    sounds = get_sounds()

    if not images:
        return

    image_file = random.choice(images)

    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)

    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()

    img = Image.open(image_file).resize((width, height))
    photo = ImageTk.PhotoImage(img)

    label = tk.Label(root, image=photo)
    label.image = photo
    label.pack(fill="both", expand=True)

    if sounds:
        try:
            winsound.PlaySound(
                random.choice(sounds),
                winsound.SND_FILENAME | winsound.SND_ASYNC
            )
        except:
            pass

    def close():
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except:
            pass
        root.destroy()

    root.after(1000, close)
    root.mainloop()

# ---------------- LOOP ----------------

def scare_loop():
    while True:
        if settings["enabled"]:
            low, high = TIME_RANGES[settings["range"]]
            time.sleep(random.randint(low, high) * 60)

            if settings["enabled"]:
                show_jumpscare()
        else:
            time.sleep(5)

# ---------------- ACTIONS ----------------

def toggle_enabled(icon=None, item=None):
    settings["enabled"] = not settings["enabled"]
    save_settings()

def set_range(name):
    settings["range"] = name
    save_settings()

def toggle_startup(icon=None, item=None):
    settings["startup"] = not settings["startup"]
    set_startup(settings["startup"])
    settings["startup"] = is_startup_enabled()
    save_settings()

def scare_now(icon=None, item=None):
    threading.Thread(target=show_jumpscare, daemon=True).start()

# ---------------- TRAY ----------------

def create_icon():
    icon_image = Image.open(resource_path("icon.png"))

    menu = pystray.Menu(
        item(lambda text: f"Enabled: {settings['enabled']}", toggle_enabled),

        item(lambda text: f"Start on boot: {settings['startup']}", toggle_startup),

        item(
            "10-30 min",
            lambda: set_range("10-30 min"),
            checked=lambda item: settings["range"] == "10-30 min"
        ),
        item(
            "30-60 min",
            lambda: set_range("30-60 min"),
            checked=lambda item: settings["range"] == "30-60 min"
        ),
        item(
            "1-2 hours",
            lambda: set_range("1-2 hours"),
            checked=lambda item: settings["range"] == "1-2 hours"
        ),

        item("Test scare", scare_now),

        item("Exit", lambda icon, item: icon.stop())
    )

    icon = pystray.Icon(APP_NAME, icon_image, APP_NAME, menu)
    icon.run()

# ---------------- MAIN ----------------

threading.Thread(target=scare_loop, daemon=True).start()
create_icon()