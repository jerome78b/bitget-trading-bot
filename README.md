# 🤖 Bitget Trading Bot V8.8
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Actively--Maintained-brightgreen)
![Bot](https://img.shields.io/badge/Type-Trading%20Bot-blueviolet)
![QA Ready](https://img.shields.io/badge/QA--Friendly-Yes-success)
## ⚠️ Used at one's own risk ⚠️
> 🇫🇷 Lire en français : [README.FR.md](README.FR.md)
> 
Automated trading bot for the **Bitget** platform, written in **Python**.  
It uses a combined strategy of **Bollinger Bands + RSI**, with smart management of **Take Profit**, **Stop Loss**, and **Partial Take Profit (TPP)**.  
The bot can run in **test/demo mode** or in **live trading**, with **Telegram notifications**.

---

## ⚠️ Requirements & Compatibility

- This bot is designed for **Futures trading only** on Bitget (not Spot).
- Only compatible with **USDT-based pairs**, such as `BTCUSDT`, `ETHUSDT`, etc.
- Requires a Bitget account with Futures API keys (demo or mainnet).
- Python 3.9 or higher is recommended.
  
## 🚀 Main Features

- 📈 Signal detection using Bollinger Bands + RSI + volatility filter
- 🤖 Automated position opening (LONG / SHORT)
- 🧠 TP / SL set as soon as a position is confirmed
- 🏹 Configurable Partial Take Profit (TPP)
- 📊 Live dashboard (price, equity, position info…)
- 🔁 Main loop with real-time display, logging and checks
- 🌐 Smart Internet disconnection handling (auto-recovery)
- 🛠️ Telegram integration (real-time alerts and notifications)
- 🧪 TEST mode available for easy simulated trades
- 
---

## 🧩 Customizable strategy

The bot uses by default a strategy based on:

- **Bollinger Bands**
- **RSI (Relative Strength Index)**
- A **volatility filter** based on band width

But it's **designed to be easily modified**:  
➡️ You can adapt **your own trading strategy** without touching the bot's core logic.

## 🔁 How to do it?

In the `BitgetBotV8.7.py` file, the following function determines the signals:

```python
def check_signal_bb_rsi(df):
    ...
    return "LONG", "SHORT", or None

```

## 📦 Installation
```
git clone https://github.com/jerome78b/bitget-trading-bot.git
cd bitget-trading-bot
pip install -r requirements.txt
```
---
## 🛠️ Configuration & Variables

You can customize the bot directly by editing the top of the `BitgetBot.py` script.

Here are the key configuration variables and what they do:

| Variable        | Type   | Description                                                                 |
|-----------------|--------|-----------------------------------------------------------------------------|
| `USE_DEMO`      | `bool` | `True` = use Bitget demo environment (testnet), `False` = live trading     |
| `TEST_MODE`     | `bool` | `True` = simulates a trade on each run, `False` = uses real BB + RSI strategy |
| `TEST_SIDE`     | `str`  | If `TEST_MODE = True`, choose `'buy'` or `'sell'` for simulated position     |
| `USE_TPP`       | `bool` | `True` = activates Partial Take Profit (TPP), `False` = disables it         |
| `SYMBOL`        | `str`  | USDT-based pair to trade, e.g. `'ETHUSDT'`, `'SOLUSDT'`                      |
| `TIMEFRAME`     | `str`  | Candlestick timeframe for analysis, e.g. `'1m'`, `'5m'`, `'15m'`, `'1h'`     |
| `LEVERAGE`      | `int`  | Leverage level applied to the position (e.g. `3`, `5`, `10`)                 |

## ✏️ Configuration
```
API_KEY=your_api_key
API_SECRET=your_api_secret
PASSPHRASE=your_passphrase
TELEGRAM_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_chat_id

```
## ❓ Why use this bot?

This project is designed to make Bitget trading automation **simple, flexible, and ready to use**, especially for beginners or QA/dev profiles who want:

- ✅ A complete working example using the Bitget API (ready out-of-the-box)
- 🧠 A customizable strategy system (plug in your own logic easily)
- 🧪 Built-in test mode to simulate trades without real money
- 💬 Real-time Telegram alerts
- 📊 Clean live dashboard (price, equity, position status)
- 🔐 Resilience to Internet cuts with auto-recovery and safe error handling

Instead of starting from scratch with raw SDKs or low-level API calls, this bot helps you **focus on your strategy**, not on technical plumbing.

Perfect for:  
- 👨‍💻 Developers looking for a QA-friendly trading bot structure  
- 📈 Traders who want to automate RSI + Bollinger-based entries  
- 🧪 Anyone learning how to build and test automated crypto strategies
---

## 📄 Licence
This project is licensed under the MIT License – free to use, modify and distribute.

## ⭐ Support the Project

If you find this trading bot useful or interesting, feel free to give it a **⭐ star** on GitHub!

It helps increase visibility, motivates development, and supports this open-source work.

➡️ [Give it a star here](https://github.com/jerome78b/bitget-trading-bot/stargazers) 🙏

## 🙋‍♂️ About
This project was developed as part of a technical demonstration in **QA testing**, **Python development**, and **automation**.  
Feel free to reach out if you're a recruiter or interested in a technical collaboration.

[![GitHub](https://img.shields.io/badge/GitHub-jerome78b-181717?logo=github)](https://github.com/jerome78b)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-jerome--profil-blue?logo=linkedin)](https://www.linkedin.com/in/jerome-bauché)

---



