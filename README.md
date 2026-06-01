# AutoEnter

A minimal Windows utility that simulates pressing the Enter key at a configurable interval. Runs quietly in the background — switch to any window and it keeps working.

## Features

- Adjustable interval (seconds)
- Start / Stop with one click or global hotkeys
- Global hotkeys: `Ctrl+Alt+1` to start, `Ctrl+Alt+2` to stop — works even when the app is in the background
- Dark minimalist UI
- Zero dependencies (uses only Python standard library + Windows API)

## Screenshot

![screenshot](screenshot.png)

## Download

Download the latest `AutoEnter.exe` from [Releases](https://github.com/HDJT/AutoEnter/releases).

## Usage

1. Run `AutoEnter.exe`
2. Set the interval (e.g. 10 seconds)
3. Click **Start** or press `Ctrl+Alt+1`
4. Switch to your target window — Enter will be pressed automatically every N seconds
5. Click **Stop** or press `Ctrl+Alt+2` to stop

## Build from source

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name AutoEnter --icon autoenter_icon.ico auto_enter_gui.py
```

The output exe will be in `dist/`.

## License

MIT
