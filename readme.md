# Roblox-Headless

A lightweight Windows utility for running Roblox clients in a **headless-style state** by hiding their windows and reducing their process priority.

The goal is to keep Roblox clients running in the background while using as little system resources and desktop space as possible.

## Features

- Hide all running Roblox clients
- Show and maximize Roblox clients with a hotkey
- Automatically lower Roblox process priority while hidden
- Restore normal process priority when clients are shown
- Kill all running Roblox clients with a hotkey
- Lightweight native Windows implementation
- Basic anti-AFK functionality is included

## Controls

| Key | Action |
|---|---|
| `RSHIFT` | Hide / show all Roblox clients |
| `CTRL+C` | Kill all Roblox clients and exit |

When Roblox clients are hidden, their process priority is lowered. When they are shown again, priority is restored to normal.

## Anti-AFK

A basic anti-AFK mechanism is currently implemented.

However, **the current implementation is not considered fully reliable yet**. Roblox input handling can change, and synthetic input does not necessarily behave exactly like real player activity.

The anti-AFK system is therefore experimental and may require further improvements.

## How It Works

The application does not create a separate Roblox environment. It operates on already-running Roblox clients through the Windows API.

The main approach is:

1. Detect running Roblox clients.
2. Locate their windows.
3. Hide or show the client windows.
4. Lower process priority while hidden.
5. Restore normal priority when unhidden.
6. Provide a hotkey to terminate all Roblox clients.

Because the actual Roblox client continues running, networking and game simulation can continue while the window is hidden.

## Project Lineage & Inspiration

Based on ideas and work from several existing Roblox headless projects:

**toastering → Stefanuk12 → sebi12391 → this project**

The focus here is on keeping the useful headless/background-client concept while providing a small, lightweight Windows utility with convenient hotkeys, dynamic priority handling, and an experimental built-in anti-AFK system.

## Disclaimer

This project is an independent implementation inspired by the projects listed above. It is not affiliated with or endorsed by the original authors or Roblox Corporation.

Use it at your own discretion. Roblox updates may change client behavior and can potentially break functionality.

## License

All associated resources. are licensed under the [MIT License](https://mit-license.org/).
