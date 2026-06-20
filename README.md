# zhaha
A Windows app that jumpscares you at random intervals, with settings synced to 0G decentralized storage. Built for the 0G Zero Cup.

# 🎃 Jumpscare App

A Windows desktop app that jumpscares you at a random, unpredictable 
interval — short (10–30 min), medium (30–60 min), or long (1–2 hours). 
Runs quietly in the system tray until it doesn't.

Built for the [0G Zero Cup](https://0g.ai/arena/zero-cup).

## ⚡ 0G Integration

Every time you change a setting (time range, enable/disable, startup), 
the app pushes your settings file to **0G's decentralized storage 
network** in the background. This isn't decorative — the app calls a 
real 0G testnet transaction every time, verifiable on-chain via the 
returned root hash / transaction hash.

This is handled by a small Node.js sidecar (`sidecar/sync.js`) that the 
Python app calls automatically — you don't need to run it manually.

## Features
- Runs in the system tray
- Fully random scare timing — no countdown, no warning
- Optional run-on-Windows-startup
- Settings synced to 0G decentralized storage on every change

## ⚠️ Disclaimer
Entertainment/prank purposes only. Don't install on someone else's PC 
without their consent. Not recommended for anyone with heart conditions, 
anxiety disorders, epilepsy, or photosensitivity.

## 🛠️ Running it yourself (for judges / developers)

This app needs **Node.js** installed (for the 0G sync) in addition to 
running the Windows `.exe`.

1. Download `JumpscareInstaller.exe` and `sidecar.zip` from the 
   [Releases](../../releases) page.
2. Run `JumpscareInstaller.exe` and complete the installation.
3. Find your installed app's folder
4. Extract `sidecar.zip` directly into that same folder
5. Install [Node.js](https://nodejs.org) if you don't have it.
6. Open a terminal in the `sidecar` folder and run: 
7. Copy `env.example` to `.env` inside `sidecar`, and fill in:
   - Your own wallet's private key (testnet only — get test tokens at 
     [faucet.0g.ai](https://faucet.0g.ai))
   - The default RPC/indexer URLs are fine to leave as-is
8. Run `Jumpscare.exe`. Change any setting from the tray menu — this 
   triggers a real push to 0G storage in the background.

## Built with
Python, Tkinter, Pillow, pystray, Node.js, `@0gfoundation/0g-storage-ts-sdk`
Coded with [0g.ai](https://0g.ai)
