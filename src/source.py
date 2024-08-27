import asyncio
from datetime import datetime
import keyboard
import os
import PIL.ImageGrab
import platform
import re
from sys import exit
import yaml

try:
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        for key, value in config.items():
            globals()[key] = value
except FileNotFoundError:
    with open('config.yaml', 'w+') as file:
        file.write("SOURCE_LOG: \nSCREENSHOT_FOLDER: \nUSE_CUSTOM_SCREENSHOT_TOOL: False\nCUSTOM_SCREENSHOT_KEY: \nREGEX_STATEMENT: \nUPDATE_RATE: 5")
        exit()


def error(msg):
    print(msg)
    print("Press enter to exit.")
    input()
    exit()


try:
    USE_CUSTOM_SCREENSHOT_TOOL = bool(USE_CUSTOM_SCREENSHOT_TOOL)  # type: ignore
except ValueError:
    error("USE_CUSTOM_SCREENSHOT_TOOL isn't True or False. Please set USE_CUSTOM_SCREENSHOT_TOOL to either True or False in config.yaml.")

try:
    UPDATE_RATE = int(UPDATE_RATE)  # type: ignore
except ValueError:
    error("UPDATE_RATE isn't an integer. Please set UPDATE_RATE to an integer in config.yaml (5 is recommended.)")

try:
    os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)  # type: ignore
except OSError:
    error("An error occured while attempting to access or create the directory specified in the SCREENSHOT_FOLDER config option in config.yaml.")
except TypeError:
    error("Please specify a folder where screenshots should be stored by setting the SCREENSHOT_FOLDER config option in config.yaml.")

if platform.system() == "Linux":
    if USE_CUSTOM_SCREENSHOT_TOOL:
        if os.geteuid() != 0:
            error("This requires superuser access on Linux while using custom screenshot tool mode because it directly accesses keyboard inputs to send screenshot key combos.")


class LogTail:
    def __init__(self, file):
        self.f = file
        self.buffer = ""

    def read_line(self):
        try:
            temp = self.f.readline()
        except UnicodeDecodeError:
            return None
        if temp != "":
            self.buffer += temp
            if self.buffer.endswith("\n"):
                line_out = self.buffer
                self.buffer = ""
                return line_out
            else:
                return None


async def main(logfile):
    if USE_CUSTOM_SCREENSHOT_TOOL:
        if CUSTOM_SCREENSHOT_KEY is None:  # type: ignore
            cos = platform.system()
            match cos:
                case "Windows":
                    SCREENSHOT_KEY = "left windows+print screen"
                case "Linux":
                    SCREENSHOT_KEY = "alt+compose"
                case "Darwin":
                    SCREENSHOT_KEY = "command+shift+3"
                case _:
                    error("Unable to detect OS. Specify what screenshot key(s) to use by setting the CUSTOM_SCREENSHOT_KEY config.")
        else:
            SCREENSHOT_KEY = f"{CUSTOM_SCREENSHOT_KEY}"  # type: ignore
            try:
                keyboard.parse_hotkey(SCREENSHOT_KEY)
            except ValueError:
                error("Unknown screenshot key or key combo. Ensure that the CUSTOM_SCREENSHOT_KEY config is correct.")
        keyboard.send("alt")

    loaded = False

    while True:
        line = LogTail(logfile).read_line()
        if line is None:
            loaded = True
            await asyncio.sleep(1.0 / UPDATE_RATE)
            continue

        if loaded:
            if re.search(f"{REGEX_STATEMENT}", line):  # type: ignore
                if USE_CUSTOM_SCREENSHOT_TOOL:
                    keyboard.send(SCREENSHOT_KEY)
                else:
                    img = PIL.ImageGrab.grab()
                    img_path = os.path.join(SCREENSHOT_FOLDER, f"{datetime.now().strftime('%y.%m.%d %H:%M:%S')}.png")  # type: ignore
                    img.save(img_path, format="PNG")
                try:
                    with open("log.txt", "a") as badlog:
                        badlog.write(line)
                except PermissionError:
                    print("Logging failed, ensure that permissions are correctly set for log.txt.")
            await asyncio.sleep(1.0 / UPDATE_RATE)

try:
    with open(SOURCE_LOG, "r") as conlog:  # type: ignore
        asyncio.run(main(conlog))
except TypeError:
    error("Please specify a path to your console.log in config.yaml.")
except OSError:
    error("Cannot find your Source console log. Please double-check the SOURCE_LOG config in config.yaml.")
