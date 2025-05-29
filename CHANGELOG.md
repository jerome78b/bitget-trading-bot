## [V8.9] - 2025-05-29
🐞 **Fix for Error 40725**
- Added a retry/backoff mechanism for error 40725 in the fetch_historical function (up to 5 attempts with exponential delay).
- 🔧 Default to swap-only
- Added options.defaultType = "swap" and defaultSubType = "linear" to force loading of swap markets only, avoiding margin-related API calls.
- ⚙️ Manual market preloading
- Use of exchange.load_markets({"type": "swap"}) before fetch_ohlcv to isolate market loading and improve robustness.
- HTTP debugging now available using the verbose flag to inspect requests and responses.
- Let me know if you want a bilingual version or need help generating a full CHANGELOG.md format.


## [V8.8] - 2025-05-27
🖥️ **Visual display of conditions when no signal**

- Added the function print_indicator_conditions():
- Color-coded display of RSI (high, low, neutral) with ✅/🔒/⚠️
- Details of Bollinger Bands (SMA, upper, lower) and volatility (width vs threshold)
- Indication of price positioning relative to the bands (🔼/🔽/➡️)**

---

## [V8.7] - 2025-05-02
🧩 **TPP Activation Option**
- Added the global variable USE_TPP = True at the top of the script.
- Allows full deactivation of Partial Take Profit (TPP) with USE_TPP = False.
- TPP (via place_partial_tpp_visible) will neither be set nor displayed if disabled.
- Display cleanup 🏹: TPP active icon now depends on USE_TPP.
- 🔒 Safety retained: the main TP/SL remains active even if USE_TPP = False.

---

## [V8.6] - 2025-04-27
✨ **Symbol Precision Management**
- Added manual detection using SYMBOL.startswith() to set PRICE_PRECISION and QUANTITY_PRECISION.
- Removed automatic CCXT call for better stability.
🛠 **Dynamic Formatting Fix**
- Fixed float formatting: float(f"{size:.{QUANTITY_PRECISION}f}") with int() conversion on precision.
🚀 **Optimizations**
- Cleaned up startup display: clearly shows the SYMBOL in use.
- Increased robustness in network handling and TP/SL errors.

---

## [V8.5] - 2025-04-26
📈 **Signal Analysis Fix**
- Signal calculation (Bollinger+RSI) now uses the **previous candle** (`df.iloc[-2]`) instead of the current one (`df.iloc[-1]`).
- Prevents false early signals before candle close.
- Updated `check_signal(df)` to use previous candle.
- Added `time.sleep(5)` after data loading ➔ ensures the candle is properly closed and synced with Bitget API.
🧪 **Robustness Tests Passed**
- Simulated signals ➔ positions only open on closed candles.
- Confirmed: no more trades triggered mid-candle (e.g., 15:42 or 16:07).

---

## [V8.4] - 2025-04-24
🌐 **Smart Network Management**
- Added proper Internet disconnection detection ➔ retry counter 1/10, 2/10, 3/10...
- Auto-blocks log messages like "Internet still down after multiple attempts" to avoid spam.
- Clean detection of Internet reconnection with automatic Telegram alert.
- Fully resets flags (`retry_count`, `internet_was_down`, `already_reported_internet_down`) upon reconnection.
🛡️ **Log Flood Protection**
- Smart cleanup of console and log files during outages.
- Strict limit on displayed errors: one network error per critical cycle.
⚡ **Main Loop Optimization**
- Fixed `retry_count` logic to allow multiple disconnection detections without bugs.
- Dynamic 30-second pause between attempts when offline.
- Resumes normal cycle without restarting the bot after a disconnection.
📈 **Robustness Tests Passed**
- Simulated outages ➔ recovery OK.
- Clean logs, no duplicates.
- 100% reliable Telegram alert after reconnection.

---

## [V8.3] - 2025-04-23
🔧 **Fix TP/SL Bitget**
- Added the delegateType field to avoid the "delegateType is error".
- TP/SL are now placed without error, logs cleaned.

---

## [V8.2] - 2025-04-23 
🚀 **Post-Trade Security (TPP + SL/TP)**
- Added `wait_for_position()` ➜ active wait until actual detection of open position.
- TPP placed **immediately after the trade**, only once.
- Direct placement of TP/SL after confirmation (no more "delegateType is error").
- Improved `TEST_MODE` ➜ only one trade triggered at startup, no loop spam.
- Refactored `__main__` ➜ same logic as main loop: signal detection, entry, TPP, TP/SL.
- Secure rounding of TP/SL prices using `round(..., 2)` to avoid Bitget API rejection.
🧪 **Tests & Checks**
- Quick test using `TEST_MODE = True` validated (LONG or SHORT).
- Clear logs: position detected ➜ TPP set ➜ TP/SL set.
- Ready for live strategy mode (TEST_MODE = False).

---

## [V8.1] - 2025-04-22 (Evening)
🧠 **Full Migration to Futures Candles via CCXT**
- Integrated historical fetch using CCXT (`fetch_ohlcv`) for Futures contracts.
- Auto-generated `SYMBOL_CCXT` from SYMBOL (format: ETH/USDT:USDT).
- Refactored `fetch_historical()` to cleanly use CCXT.
- Used `SYMBOL_CCXT` in `prepare_data()` function.
- Fully supports changing SYMBOL and TIMEFRAME without editing code.
- Auto-validation of symbol format to prevent CCXT errors.
🧼 **Config Refactor**
- Auto-conversion of symbol to CCXT-compatible format.
- Removed unnecessary variable redefinitions.
🧪 **Tests & Validations**
- Verified `df.iloc[-1]` returns the latest candle (e.g., 23:30).
- Confirmed CCXT data is live and synced.
- Removed obsolete testnet/native blocks.
🐛 **Bug Fix (from V8)**
- Fixed `TypeError` in tp_price calculation (entry was a dict).

---

## [V8] - 2025-04-22
🛠️ **Complete Rewrite of Logs & Errors**
- Refactored logs: single-line format, removed duplicates.
- `send_error_once()` system: sends errors only once (log + Telegram).
- Anti-spam for all errors (TP, SL, TPP, loop...).
- Clean regrouping of TP/SL errors into one line.
- Improved `place_partial_tpp_visible` with integrated logging + Telegram.
- Fetched real price via `detect_current_position_bitget`.
- Cleaned error handling in main loop (Telegram tracebacks).
- Optimized logging and Telegram alerts for TPP.

---

## [V7] - 2025-04-21
📈 **Cycle & Strategy Improvements**
- Live ETH price display with variation on each cycle.
- Full logging and Telegram integration.
- Integrated Bollinger + RSI strategy (indicator checks).
- Auto-clears terminal every X candles.

---

## [V6] - 2025-04-18
🎯 **Improved TPP & Auto Monitoring**
- TPP placed only at trade opening.
- SL/TP auto-repositioned if missing on each cycle.
- More robust order monitoring logic.

---

## [V5] - 2025-04-15
🔁 **Main Loop Implementation**
- Implemented the bot’s core (loop/check cycle).
- Full dashboard display (price, equity, position, etc.).
- Added partial exit with visible status (executed / pending).

---

## [V4] - 2025-04-13
💰 **Active Position Management**
- Implemented Partial Take Profit (functional).
- Checks for existing position before opening a new one.

---

## [V3] - 2025-04-10
🎯 **TP/SL and Auto Position Sizing**
- Auto-rounds position size to 2 decimals.
- Added TP (Take Profit) and SL (Stop Loss) handling.

---

## [V2] - 2025-04-07
⚙️ **Technical Foundations**
- Implemented dynamic leverage.
- Added support for LONG and SHORT positions.
- Full leverage and margin mode logic implemented.
