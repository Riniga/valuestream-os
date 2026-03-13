import time
from pyvda import VirtualDesktop

DESKTOP_NAMES = {
    1: "Leveranskoordinator",
    2: "Processledare",
    3: "C7 Projects",
    4: "Betong"
}

last_number = None

def on_desktop_changed(number, name):
    print(f"Bytte till Desktop {number}: {name}")
    if name == "Processledare":
        print("=> Kör action för Processledare här")
        # t.ex. starta Toggl-timer, visa notis, starta app, osv.

while True:
    current = VirtualDesktop.current()
    number = current.number

    if number != last_number:
        last_number = number
        name = DESKTOP_NAMES.get(number, f"Desktop {number}")
        on_desktop_changed(number, name)

    time.sleep(2)