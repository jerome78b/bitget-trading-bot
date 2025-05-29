import time
import json
import hmac
import hashlib
import base64
import requests
import ccxt
import colorama
from colorama import init, Fore, Style
import pandas as pd
from datetime import datetime
import os
import logging 
import random
import traceback
import urllib3
from ccxt.base.errors import NetworkError


#=======================================================#
colorama.init(autoreset=True)
logging.basicConfig(
    filename="bitget_bot.log",  # 💾 
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding='utf-8'
    )
# ============== NETWORK DISCONNECTION MANAGEMENT ==============
MAX_RETRIES = 10   # Number of retry attempts before alert
RETRY_DELAY = 30   # Delay in seconds between retry attempts
# =============================================================

# === CURRENT BOT VERSION ===
BOT_VERSION = "8.9"
BOT_LAST_UPDATE = "2025-05-29"
BOT_CHANGELOG = [
    "✨ Symbol precision handling",
    "📈 Signal analysis fix",
    "🐞 Fix erreur 40725",
    "🎯 Intelligent grouping of TP/SL errors",
    "🧠 Complete migration to Futures candles via CCXT",
    "🌐 Smart network management",
]

###############################################################################
##                                                                           ##
##                   🛠️ Configuration & Variables              
##                                                                           ##
###############################################################################

# ======== 🧰 General Bot Configuration ======== #

USE_DEMO = True              # Demo mode = True, Mainnet = False
TEST_MODE = False            # False = run live strategy (BB + RSI), True = force a trade with TEST_SIDE without waiting for a signal
TEST_SIDE = 'buy'            # 'buy' or 'sell' for test trades
SYMBOL = "ETHUSDT"           # Trading pair, e.g., 'ETHUSDT', 'BTCUSDT'
TIMEFRAME = "15m"            # '15m', '30m', '45m', '1h', etc.
LEVERAGE = 3                 # Desired leverage
MARGIN_MODE = 'crossed'      # 'crossed' or 'isolated'
CYCLE_COUNT = 20          # Number of cycles before auto-clearing the console
LOOP_INTERVAL = 60        # Seconds between each loop iteration
TRACK_SIGNALS = True      # Set to False to disable signal tracking
TELEGRAM_ENABLED = True   # Enable or disable Telegram notifications

# ======== 🎯 Position Management & Strategy Settings ======== #

CAPITAL_ENGAGEMENT = 0.10    # Percentage of capital to allocate (10%)
USE_TPP = False                 # False = disable, True = enable Partial Take Profit
TRAIL_TRIGGER = 2.3 / 100       # Trailing trigger threshold (2.3%)
PARTIAL_EXIT_FRACTION = 0.85    # Fraction of position to exit (85%)
TP_PERCENT_LONG = 4.1           # Take Profit percentage for long positions
SL_PERCENT_LONG = 1.5           # Stop Loss percentage for long positions
TP_PERCENT_SHORT = 4.0          # Take Profit percentage for short positions
SL_PERCENT_SHORT = 1.5          # Stop Loss percentage for short positions

# ======== 📊 Technical Indicator Settings ======== #

BOLL_PERIOD = 34               # Period used for Bollinger Bands calculation (e.g., 34)
BOLL_MULT = 2.0                # Standard deviation multiplier to set the width of Bollinger Bands
RSI_PERIOD = 14                # Period used for calculating the RSI (Relative Strength Index)
RSI_HIGH_THRESHOLD = 40        # Threshold above which RSI confirms a LONG signal (e.g., > 40)      
RSI_LOW_THRESHOLD = 60         # Threshold below which RSI confirms a SHORT signal (e.g., < 60)        
WIDTH_PERIOD = 21              # Period used to measure bandwidth (used as a volatility filter)
VOL_MULT = 1.0                 # Multiplier applied to volatility to validate trade conditions

# ======== ✏️ Configuration ======== #

TELEGRAM_TOKEN = "your_api_key"       
TELEGRAM_CHAT_ID = "your_api_secret"      
API_KEY = "your_passphrase"
API_SECRET = "your_telegram_token"
PASSPHRASE = "your_chat_id"          


#========================================================#
BASE_URL = "https://api.bitget.com"  
SYMBOL_CCXT = SYMBOL
if "/" not in SYMBOL_CCXT:
    SYMBOL_CCXT = SYMBOL_CCXT.replace("USDT", "/USDT:USDT")
global retry_count
retry_count = 0    
#========================================================#


# === Set precision automatically based on the symbol ===

if SYMBOL.startswith("BTC"):
    PRICE_PRECISION = 1      # Price precision for BTC pairs (e.g., 94 298.2 USDT has 1 decimal; ETH prices often use 3 decimals, e.g., 1 524.456 USDT)
    QUANTITY_PRECISION = 4   # Quantity precision for BTC (e.g., 2.2545 BTC has 4 decimals; ETH quantities often use 2, e.g., 4.28 ETH)
elif SYMBOL.startswith("ETH"): 
    PRICE_PRECISION = 2
    QUANTITY_PRECISION = 2
elif SYMBOL.startswith("SOL"):
    PRICE_PRECISION = 3
    QUANTITY_PRECISION = 1
elif SYMBOL.startswith("XRP"):
    PRICE_PRECISION = 4
    QUANTITY_PRECISION = 0
elif SYMBOL.startswith("DOGE"):
    PRICE_PRECISION = 5
    QUANTITY_PRECISION = 0
else:
    PRICE_PRECISION = 2
    QUANTITY_PRECISION = 2  


# ===================== STRATÉGIES ===================== # 

def compute_rsi(series: pd.Series, period: int) -> pd.Series:
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
    # Should this be modified when you change strategies?
    # ❌ No — it can remain common (base indicator)

def check_signal_bb_rsi(df: pd.DataFrame):
    """
    Applique la stratégie Bollinger + RSI + filtre de volatilité.
    Retourne 'LONG', 'SHORT' ou None.
    """
    if df is None or len(df) < max(BOLL_PERIOD, WIDTH_PERIOD) + 5:
        return None

    df = df.copy()
    df['SMA'] = df['close'].rolling(window=BOLL_PERIOD).mean()
    df['STD'] = df['close'].rolling(window=BOLL_PERIOD).std()
    df['upper'] = df['SMA'] + df['STD'] * BOLL_MULT
    df['lower'] = df['SMA'] - df['STD'] * BOLL_MULT

    df['width'] = (df['upper'] - df['lower']) / df['SMA']
    df['width_MA'] = df['width'].rolling(window=WIDTH_PERIOD).mean()
    df['width_STD'] = df['width'].rolling(window=WIDTH_PERIOD).std()
    df['vol_threshold'] = df['width_MA'] + VOL_MULT * df['width_STD']

    df['RSI'] = compute_rsi(df['close'], RSI_PERIOD)

    last = df.iloc[-2]
    
    # Entry conditions
    if last['width'] > last['vol_threshold']:
        if last['RSI'] > RSI_HIGH_THRESHOLD and last['close'] > last['upper']:
            return "LONG"
        elif last['RSI'] < RSI_LOW_THRESHOLD and last['close'] < last['lower']:
            return "SHORT"

    return None
    # Should this be modified when you change strategies?
    # ✅ YES

def check_signal(df): 
    last = df.iloc[-2]
    print(f"Close={last.close:.{PRICE_PRECISION}f}, Upper={last.upper:.{PRICE_PRECISION}f}, Lower={last.lower:.{PRICE_PRECISION}f}, RSI={last.RSI:.2f}")
    if last.close > last.upper and last.RSI > RSI_HIGH_THRESHOLD:
        return 'LONG'
    if last.close < last.lower and last.RSI < RSI_LOW_THRESHOLD:
        return 'SHORT'
    return None
     # Should this be modified when you change strategies?
    # ✅ YES

def prepare_data(): 
    try:
        return fetch_historical(SYMBOL_CCXT, TIMEFRAME, 200)
    except (requests.exceptions.ConnectionError, urllib3.exceptions.HTTPError, NetworkError) as e:
        if not already_reported_internet_down:
            logging.warning(f"🌐 Network error during fetch_historical: {e}")
        raise ConnectionError("Network error in prepare_data()")
    # Should this be modified when you change strategies?
    # ⚠️ TO BE ADAPTED based on the strategy

def fetch_historical(symbol="ETH/USDT:USDT", timeframe="15m", limit=200):
    """
    Récupère les bougies swap via CCXT, en swap-only et avec retry/backoff sur l’erreur 40725.
    """
    exchange = ccxt.bitget({
        "apiKey": API_KEY,
        "secret": API_SECRET,
        "timeout": 5000,
        "enableRateLimit": True,
        # 1) FORCE swap-only → plus d’appel à l’endpoint margin
        "options": {
            "defaultType": "swap",
            "defaultSubType": "linear",
        },
        # "verbose": True,  # décommentez pour debug HTTP
    })

    max_retries = 5
    delay = 1
    for attempt in range(1, max_retries + 1):
        try:
            # 2) on charge manuellement les marchés swap
            exchange.load_markets({"type": "swap"})
            # 3) on récupère les OHLCV
            ohlcv = exchange.fetch_ohlcv(
                symbol,
                timeframe=timeframe,
                limit=limit
            )
            break
        except ccxt.ExchangeError as e:
            # on ne retry que sur le code 40725
            if '40725' in str(e):
                print(f"[fetch_historical] Tentative {attempt} – Erreur 40725, retry dans {delay}s…")
                time.sleep(delay)
                delay *= 2
            else:
                # toute autre erreur doit remonter
                raise
    else:
        raise RuntimeError("fetch_historical a échoué après plusieurs tentatives (40725)")

    # === mise en forme DataFrame inchangée ===
    df = pd.DataFrame(ohlcv, columns=["ts", "open", "high", "low", "close", "vol"])
    df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    df.set_index("ts", inplace=True)

    df['SMA']         = df['close'].rolling(window=BOLL_PERIOD).mean()
    df['STD']         = df['close'].rolling(window=BOLL_PERIOD).std()
    df['upper']       = df['SMA'] + BOLL_MULT * df['STD']
    df['lower']       = df['SMA'] - BOLL_MULT * df['STD']
    df['width']       = (df['upper'] - df['lower']) / df['SMA']
    df['width_MA']    = df['width'].rolling(window=WIDTH_PERIOD).mean()
    df['width_STD']   = df['width'].rolling(window=WIDTH_PERIOD).std()
    df['vol_threshold'] = df['width_MA'] + VOL_MULT * df['width_STD']
    df['RSI']         = compute_rsi(df['close'], RSI_PERIOD)

    return df.dropna()

    # Should this be modified when you change strategies?
    # ⚠️ TO BE ADAPTED based on the strategy

# ===================== UTILITAIRES ==================== # 

def get_timestamp():
    return str(int(time.time() * 1000))

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def pre_hash(ts, method, path, body):
    return f"{ts}{method.upper()}{path}{body or ''}"

def sign(message, secret):
    return base64.b64encode(hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()).decode()

def send_signed_request(path, method='GET', params=None, body=None):
    ts = get_timestamp()
    body_str = json.dumps(body, separators=(',', ':'), sort_keys=True) if body else ''
    req_path = path

    qs = ''
    if method == 'GET' and params:
        qs = '&'.join(f"{k}={params[k]}" for k in sorted(params))
        req_path = f"{path}?{qs}"

    message = f"{ts}{method.upper()}{req_path}{body_str}"

    signature = sign(message, API_SECRET)

    headers = {
        'ACCESS-KEY': API_KEY,
        'ACCESS-SIGN': signature,
        'ACCESS-TIMESTAMP': ts,
        'Content-Type': 'application/json',
        'locale': 'en-US'
    }
    if PASSPHRASE:
        headers['ACCESS-PASSPHRASE'] = PASSPHRASE
    if USE_DEMO:
        headers['paptrading'] = '1'

    url = BASE_URL + path
    if method == 'GET' and params:
        url += '?' + qs

    resp = requests.request(method, url, headers=headers, data=body_str if method == 'POST' else None)
    try:
        return resp.json()
    except ValueError:
        return {'error': resp.status_code, 'text': resp.text}   

def set_margin_mode(symbol, mode):
    path = '/api/v2/mix/account/set-margin-mode'
    body = {
        'symbol': symbol,
        'productType': 'SUSDT-FUTURES' if USE_DEMO else 'USDT-FUTURES',
        'marginCoin': symbol[-4:].upper(),
        'marginMode': mode
    }
    res = send_signed_request(path, 'POST', body=body)
    if res.get("code") == "00000":
        print("✅ Margin mode configured")
    else:
        send_error_once("❌ Margin mode configuration error")

    return res

def set_leverage(symbol, leverage, mode):
    path = '/api/v2/mix/account/set-leverage'
    base = {
        'symbol': symbol,
        'productType': 'SUSDT-FUTURES' if USE_DEMO else 'USDT-FUTURES',
        'marginCoin': symbol[-4:].upper()
    }
    if mode == 'isolated':
        for side in ['long','short']:
            body = {**base, 'leverage': str(leverage), 'holdSide': side}
            res = send_signed_request(path, 'POST', body=body)
            print(f"Leverage {side} set:", res)
    else:
        body = {**base, 'leverage': str(leverage)}
        res = send_signed_request(path, 'POST', body=body)
        if res.get("code") == "00000":
            print("✅ Cross leverage configured")
        else:
            send_error_once(f"❌ Cross leverage configuration error: {res.get('msg')}")
    return res

def place_market_order(symbol, qty, side, mode):
    path = '/api/v2/mix/order/place-order'
    side_str = 'long' if side == 'buy' else 'short'
    size = round(qty, QUANTITY_PRECISION)
    print(f"📥 Sending market order : {side_str.upper()} {size:.{QUANTITY_PRECISION}f} {symbol} (mode={mode})")
    body = {
        'productType': 'SUSDT-FUTURES' if USE_DEMO else 'USDT-FUTURES',
        'symbol': symbol,
        'marginMode': mode,
        'marginCoin': symbol[-4:].upper(),
        'size': str(size),
        'side': side,
        'tradeSide': 'open',
        'orderType': 'market',
        'force': 'gtc',
        'clientOid': get_timestamp(),
        'reduceOnly': 'NO'
    }
    resp = send_signed_request(path, 'POST', body=body)

    if resp.get("code") == "00000":
        entry_price = get_entry_price_from_position(symbol)
        logging.info(f"POSITION OPENED: {side_str.upper()} {size:.{QUANTITY_PRECISION}f} {symbol} at {entry_price:.{PRICE_PRECISION}f} USDT")

        if TELEGRAM_ENABLED:
            send_telegram_message(
                f"📥 *NEW POSITION OPENED*\n"
                f"⚙️ Leverage: {LEVERAGE}x\n"
                f"Type: *{side_str.upper()}*\n"
                f"Qty: *{size:.{QUANTITY_PRECISION}f}* {symbol}\n"
                f"Price: `{entry_price:.{PRICE_PRECISION}f}`"
            )
    else:
        err = resp.get("msg", "Unknown error")
        send_error_once(f"❌ Trade failed: {err}")
    data = resp.get('data') or {}

    return data.get('orderId'), size

def get_entry_price_from_position(symbol):
    in_pos, _side, entry_price, *_ = wait_for_position(symbol)
    return float(entry_price) if in_pos else 0.0

def is_position_open(symbol):
    path = "/api/v2/mix/position/single-position"
    for side in ['long', 'short']:
        params = {
            "symbol": symbol,
            "marginCoin": symbol[-4:].upper(),
            "productType": 'SUSDT-FUTURES' if USE_DEMO else 'USDT-FUTURES',
            "holdSide": side
        }
        res = send_signed_request(path, "GET", params=params)
        print(f"📦 API RAW {side.upper()} → {res}")

        data = res.get('data')
        if isinstance(data, list):  
            for pos in data:
                if pos['symbol'] == symbol and float(pos.get('total', 0)) > 0:
                    print(f"🚨 {side.upper()} position detected: total = {pos['total']}")
                    return True
        elif isinstance(data, dict):
            if float(data.get('total', 0)) > 0:
                print(f"🚨 {side.upper()} position detected: total = {data['total']}")
                return True

    print("✅ No position detected (long/short = 0).")
    return False

def set_full_tp_sl(symbol: str,
                   side: str,
                   tp_price: float,
                   sl_price: float,
                   demo: bool,
                   mode: str):
    """
    Place le TP et SL “full position” via plan orders V2.
    """
    path = '/api/v2/mix/order/place-tpsl-order'
    product_type = 'SUSDT-FUTURES' if demo else 'USDT-FUTURES'

    common = {
        "symbol":      symbol,
        "productType": product_type,
        "marginMode":  mode,
        "marginCoin":  symbol[-4:].upper(),
        "holdSide":    side,
        "executePrice": "0",             
        "delegateType": "close"           
    }

    tp_body = {
        **common,
        "planType":     "pos_profit",
        "triggerPrice": f"{tp_price:.{PRICE_PRECISION}f}",
        "triggerType":  "mark_price",
        "clientOid": f"tp_{get_timestamp()}_{random.randint(1000,9999)}"
    }

    sl_body = {
        **common,
        "planType":     "pos_loss",
        "triggerPrice": f"{sl_price:.{PRICE_PRECISION}f}",
        "triggerType":  "mark_price",
        "clientOid": f"sl_{get_timestamp()}_{random.randint(1000,9999)}"
    }

    tp_res = send_signed_request(path, 'POST', body=tp_body)
    sl_res = send_signed_request(path, 'POST', body=sl_body)

    
    errors = []
    if tp_res.get("code") != "00000":
        errors.append(f"TP ➜ {tp_res.get('msg', 'Unknown error')}")
    if sl_res.get("code") != "00000":
        errors.append(f"SL ➜ {sl_res.get('msg', 'Unknown error')}")
    if errors:
        send_error_once("❌ TP/SL failed: " + " | ".join(errors))

    if tp_res.get("code") == "00000" and sl_res.get("code") == "00000":
        if TELEGRAM_ENABLED:
            send_telegram_message(
                f"🎯 *TP/SL auto placed*\n"
                f"TP: `{tp_price:.{PRICE_PRECISION}f}` USDT\n"
                f"SL: `{sl_price:.{PRICE_PRECISION}f}` USDT"
            )
        logging.info(f"TP/SL placed: TP={tp_price:.{PRICE_PRECISION}f} SL={sl_price:.{PRICE_PRECISION}f}")

    return tp_res, sl_res

def place_partial_tpp_visible(symbol, side, trigger_price, qty_limit, mode):
    print(f"🎯 Placing TPP : {qty_limit:.{QUANTITY_PRECISION}f} {symbol} @ {trigger_price:.{PRICE_PRECISION}f} USDT")
    path = "/api/v2/mix/order/place-tpsl-order"
    body = {
        "productType": 'SUSDT-FUTURES' if USE_DEMO else 'USDT-FUTURES',
        "symbol": symbol,
        "marginMode": mode,
        "marginCoin": symbol[-4:].upper(),
        "holdSide": side,  # 'long' ou 'short'
        "planType": "profit_plan",
        "triggerPrice": f"{trigger_price:.{PRICE_PRECISION}f}",
        "triggerType": "mark_price",
        "size": str(round(qty_limit, QUANTITY_PRECISION)),
        "orderType": "market",
        "clientOid": get_timestamp()
    }

    res = send_signed_request(path, "POST", body=body)

    if res.get("code") == "00000":
        logging.info(f"TPP Placing : {qty_limit:.{QUANTITY_PRECISION}f} {symbol} à {trigger_price:.{PRICE_PRECISION}f} USDT")
        if TELEGRAM_ENABLED:
            send_telegram_message(
                f"🎯 *TPP successfully placed*\n"
                f"Qté : `{qty_limit:.{QUANTITY_PRECISION}f}` {symbol}\n"
                f"Prix : `{trigger_price:.{PRICE_PRECISION}f}` USDT"
            )
    else:
        err_msg = res.get("msg", "Unknown error")
        send_error_once(f"❌ TPP failed : {err_msg}")


    return res

def fetch_dashboard_info(symbol: str) -> dict:
    """
    # Fetch and return a structured dictionary with:
    #   - timestamp
    #   - mark_price
    #   - equity           (accountEquity)
    #   - margin_balance   (equity - available)
    #   - available
    #   - initial_margin   (position.marginSize)
    #   - initial_margin_ratio
    # Always using USDT-FUTURES + header paptrading=1 for sandbox.
    """
    product = 'USDT-FUTURES'

    # 1) Solde du compte
    resp_account = send_signed_request(
        '/api/v2/mix/account/accounts',
        'GET',
        {'productType': product}
    )
    if not resp_account.get('data'):
        raise RuntimeError("Unable to retrieve account data")

    # 2) Prix mark
    resp_market = send_signed_request(
        '/api/v2/mix/market/symbol-price',
        'GET',
        {'symbol': symbol, 'productType': product}
    )
    if not resp_market.get('data'):
        raise RuntimeError("Unable to retrieve mark price")

    # 3) Position (may be empty)
    resp_position = send_signed_request(
        '/api/v2/mix/position/single-position',
        'GET',
        {
            'symbol': symbol,
            'marginCoin': symbol[-4:].upper(),
            'productType': product
        }
    )

    # --- parsing account ---
    acct = resp_account['data'][0]
    equity    = float(acct.get('accountEquity', 0))    # total equity :contentReference[oaicite:2]{index=2}&#8203;:contentReference[oaicite:3]{index=3}
    available = float(acct.get('available', 0))       
    margin_balance = equity - available               
    
    # --- parsing mark price ---
    mk = resp_market['data'][0]
    mark_price = float(mk['markPrice'])

    # --- parsing initial margin (position) ---
    pos = resp_position.get('data')
    if isinstance(pos, list):
        initial_margin = float(pos[0].get('marginSize', 0)) if pos else 0.0
    else:
        initial_margin = float(pos.get('marginSize', 0)) if pos else 0.0

    # --- calcul IMR ---
    imr_ratio = (initial_margin / equity) * 100 if equity > 0 else 0.0
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    disponible = equity - initial_margin

    return {
        'timestamp': timestamp,
        'mark_price': mark_price,
        'equity': equity,  
        'available': available,
        'disponible': disponible,
        'margin_balance': margin_balance,
        'initial_margin': initial_margin,
        'initial_margin_ratio': imr_ratio
    }

def print_dashboard(info: dict, symbol: str):
    print("=" * 18 + f" Version {BOT_VERSION} " + "=" * 18)
    print(f"📅 {info['timestamp']} | Price {symbol}: {info['mark_price']:.{PRICE_PRECISION}f} USDT")
    print(f"🏦 Total Capital        : {info['available']:.2f} USDT")
    print(f"💰 USDT Balance         : {info['equity']:.2f} USDT")
    print(f"💸 Available Funds      : {info['disponible']:.2f} USDT")
    print(f"⚖️  Unrealized P&L       : {info['margin_balance']:.2f} USDT") 
    print(f"📏 Initial Margin       : {info['initial_margin']:.2f} USDT")
    print(f"📊 Initial Margin %     : {info['initial_margin_ratio']:.2f} %")
    print("=" * 50)

def print_indicator_conditions(df):
    """
    # Display the status of indicators (RSI, Bollinger, volatility) with color formatting
    # when no trade signal is detected.
    """
    last = df.iloc[-2]
    # RSI
    rsi = last['RSI']
    if rsi > RSI_HIGH_THRESHOLD:
        print(Fore.GREEN + f"✅ High RSI   : {rsi:.2f} > {RSI_HIGH_THRESHOLD}" + Style.RESET_ALL)
    elif rsi < RSI_LOW_THRESHOLD:
        print(Fore.GREEN + f"✅ Low RSI    : {rsi:.2f} < {RSI_LOW_THRESHOLD}" + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + f"🔒 Neutral RSI: {rsi:.2f}" + Style.RESET_ALL)

    # Bollinger Bands & vol
    sma = last['SMA']
    upper = last['upper']
    lower = last['lower']
    width = last['width']
    threshold = last['vol_threshold']
    print(f"📏 Upper Band: {upper:.{PRICE_PRECISION}f}, Lower Band: {lower:.{PRICE_PRECISION}f}, SMA: {sma:.{PRICE_PRECISION}f}")
    if width > threshold:
        print(Fore.GREEN + f"✅ Volatility OK: width {width:.4f} > threshold {threshold:.4f}" + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + f"⚠️  Low volatility: width {width:.4f} ≤ threshold {threshold:.4f}" + Style.RESET_ALL)

    # Breakout conditions
    price = last['close']
    if price > upper:
        print(Fore.CYAN + f"🔼 Price above upper band: {price:.{PRICE_PRECISION}f} > {upper:.{PRICE_PRECISION}f}" + Style.RESET_ALL)
    elif price < lower:
        print(Fore.CYAN + f"🔽 Price below lower band: {price:.{PRICE_PRECISION}f} < {lower:.{PRICE_PRECISION}f}" + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + f"➡️  Price between bands: {price:.{PRICE_PRECISION}f}" + Style.RESET_ALL)

    print(Fore.MAGENTA + "👀 Waiting for the next signal..." + Style.RESET_ALL)

def live_price_preview_simple(symbol="ETHUSDT", interval_sec=2, total_duration_sec=60):
    steps = total_duration_sec // interval_sec
    last_price = None
    last_fetch_failed = False

    for _ in range(steps):
        try:
            info = fetch_dashboard_info(symbol)
            price = info.get('mark_price')

            if price is not None:
                if last_price is not None:
                    if price > last_price:
                        print(f"\033[92m🔼 Futures price {symbol}: {price:.{PRICE_PRECISION}f} USDT\033[0m")
                    elif price < last_price:
                        print(f"\033[91m🔽 Futures price {symbol}: {price:.{PRICE_PRECISION}f} USDT\033[0m")
                    else:
                        print(f"➡️  Futures price {symbol}: {price:.{PRICE_PRECISION}f} USDT")
                else:
                    print(f"💹 Futures price {symbol}: {price:.{PRICE_PRECISION}f} USDT")

                last_price = price
                last_fetch_failed = False
            else:
                if not last_fetch_failed:
                    logging.warning("❌ Invalid data received in fetch_dashboard_info()")
                    print("❌ Invalid data received in fetch_dashboard_info()")
                last_fetch_failed = True

        except Exception as e:
            if not last_fetch_failed:
                logging.warning(f"❌ Error retrieving price: {e}")
                print(f"❌ Error retrieving price: {e}")
            last_fetch_failed = True

        time.sleep(interval_sec)

def detect_current_position_bitget(symbol: str):
    """
    Renvoie un tuple :
      (in_position: bool,
       side: str,              # 'LONG' ou 'SHORT'
       entry_price: float,
       size: float,
       full_tp: float or None,
       full_sl: float or None,
       partial_tps: List[Tuple[float, float]])  # list of (triggerPrice, size)
    """
    product = 'USDT-FUTURES'

    # 1) Position courante
    resp_pos = send_signed_request(
        '/api/v2/mix/position/single-position', 'GET',
        {
            'symbol': symbol,
            'marginCoin': symbol[-4:].upper(),
            'productType': product
        }
    )
    data = resp_pos.get('data') or []
    pos = None
    if isinstance(data, list):
        for p in data:
            if float(p.get('total', 0)) > 0:
                pos = p
                break
    elif isinstance(data, dict) and float(data.get('total', 0)) > 0:
        pos = data

    if not pos:
        return False, None, None, None, None, None, []

    # 2) Infos  position
    side        = 'LONG' if pos.get('holdSide') == 'long' else 'SHORT'
    entry_price = float(pos.get('openPriceAvg', 0))
    size        = float(pos.get('total', 0))

    # 3) Retrieve all plan orders of type profit_loss
    resp_plan = send_signed_request(
        '/api/v2/mix/order/orders-plan-pending', 'GET',
        {
            'symbol': symbol,
            'productType': product,
            'planType': 'profit_loss'
        }
    )
    raw = resp_plan.get('data')
    if isinstance(raw, dict) and 'entrustedList' in raw:
        plans = raw['entrustedList'] or []
    elif isinstance(raw, list):
        plans = raw or []
    else:
        plans = []

    # 4) Separate full TP/SL and collect (triggerPrice, size) for TPP orders
    full_tp     = None
    full_sl     = None
    partial_tps = []
    for o in plans:
        if not isinstance(o, dict):
            continue
        pt = o.get('planType')
        # Trigger price
        try:
            price = float(o.get('triggerPrice', 0))
        except:
            continue
        # Plan quantity (base coin)
        try:
            qty = float(o.get('size', 0))
        except:
            qty = 0.0

        if pt == 'pos_profit':
            full_tp = price
        elif pt == 'pos_loss':
            full_sl = price
        elif pt == 'profit_plan':
            partial_tps.append((price, qty))

    return True, side, entry_price, size, full_tp, full_sl, partial_tps
    
def escape_markdown(text: str) -> str:
    import re
    escape_chars = r"[_*[\]()~`>#+\-=|{}.!]"
    return re.sub(f"({escape_chars})", r"\\\1", text)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"  # ou "HTML"
    }
    try:
        requests.post(url, data=data)
    except Exception as e:
        logging.warning(f"Erreur Telegram : {e}")
        return False
    return True

def print_order_result(prefix: str, response: dict):
    """
    # Handle display/logging/Telegram alert for an API response
    """
    if response.get("code") == "00000":
        order_id = response.get("data", {}).get("orderId")
        msg = f"✅ {prefix} Successful"
        if order_id:
            msg += f" (Order ID: {order_id})"
        print(msg)
        logging.info(msg)
    else:
        err_msg = response.get("msg", "Erreur inconnue")
        msg = f"🚫 {prefix} Failed : {err_msg}"
        print(msg)
        send_error_once(msg)

        if TELEGRAM_ENABLED:
            escaped = escape_markdown(err_msg)
            send_telegram_message(
                f"🚨 *Bitget API Error : {prefix} Failed*\n"
                f"`{escaped}`"
            )

def send_error_once(message: str):
    global last_error_sent
    if message != last_error_sent:
        logging.error(message)
        if TELEGRAM_ENABLED:
            send_telegram_message(f"🚨 *Error detected* :\n`{escape_markdown(message)}`")
        last_error_sent = message

def display_bot_header():
    print(colorama.Fore.BLUE +"=" * 60 + colorama.Style.RESET_ALL)
    print(f"🤖 Bitget Trading Bot - Version {BOT_VERSION} (maj {BOT_LAST_UPDATE})")
    print(colorama.Fore.RED +"=" * 60 + colorama.Style.RESET_ALL)
    for line in BOT_CHANGELOG:
        print("• " + line)
    print(colorama.Fore.RED +"=" * 60 + "\n"+ colorama.Style.RESET_ALL)

def track_signal_activity(signal, in_pos):
    global signals_detected, signals_taken, signals_ignored

    if not TRACK_SIGNALS:
        return

    if signal in ['LONG', 'SHORT']:
        signals_detected += 1
        if in_pos:
            signals_ignored += 1
        else:
            signals_taken += 1

            print(
            f"📊 Signals detected: {Fore.GREEN}{signals_detected}{Style.RESET_ALL} | "
            f"Executed: {Fore.BLUE}{signals_taken}{Style.RESET_ALL} | "
            f"Ignored: {Fore.RED}{signals_ignored}{Style.RESET_ALL}"
        )

def wait_for_position(symbol, retries=10, delay=0.2):
    for _ in range(retries):
        result = detect_current_position_bitget(symbol)
        if result and result[0]:  # in_pos == True
            return result
        time.sleep(delay)
    return None, None, None, None, None, None, []

#=============== VARIABLES GLOBALES ===============
signals_detected = 0
signals_taken = 0
signals_ignored = 0
last_error_sent = None
prev_qty = None
partial_status = 'en attente'
cycle_count = 0  # compteur de cycles
just_placed_tp_sl = False
retry_count = 0
internet_was_down = False
internet_alert_sent = False  # ← Ajoute ça ici 🧠
already_reported_internet_down = False
internet_ko_logged = False  # ✅ Nouveau flag
#==================================================

if __name__ == '__main__':           
    print("\n🚀 Launching the bot...\n")
    display_bot_header()
    print(f"🧠 Active parameters: {SYMBOL_CCXT} | TF = {TIMEFRAME} | Leverage = {LEVERAGE}x")
    df_hist = prepare_data()
    print("\n📁 Indicators loaded (last candle):")
    print(df_hist.iloc[-1][['close', 'RSI', 'upper', 'lower', 'width', 'vol_threshold']])

    
    sig = TEST_SIDE if TEST_MODE else check_signal_bb_rsi(df_hist)

    in_pos, *_ = detect_current_position_bitget(SYMBOL)
    if in_pos:
        print('🚫 A position is already detected (manual or automatic). No new trade will be executed.')
    elif sig is None:
        print("👀 No signal detected. The bot is waiting for the next cycle.")
    else:
        # Automatic position entry
        acc = send_signed_request('/api/v2/mix/account/accounts', 'GET', {'productType': 'USDT-FUTURES'})
        entry = acc['data'][0]
        bal = float(entry.get('available') or entry.get('isolatedMaxAvailable'))

        set_margin_mode(SYMBOL, MARGIN_MODE)
        set_leverage(SYMBOL, LEVERAGE, MARGIN_MODE)

        price = df_hist['close'].iloc[-1]
        margin_amount = bal * CAPITAL_ENGAGEMENT
        size = margin_amount * LEVERAGE / price
        size = float(f"{size:.{QUANTITY_PRECISION}f}")

        side = TEST_SIDE if TEST_MODE else ('buy' if sig == 'LONG' else 'sell')
        side_str = 'long' if side == 'buy' else 'short'  
        
        oid, resp = place_market_order(SYMBOL, size, side, MARGIN_MODE)
        # 🕒 Pause to allow the position to activate on Bitget
        time.sleep(0.2)

        # 🛰️ Retrieve actual position info as done in the main loop
        in_pos, side_detected, entry_price, qty, *_ = detect_current_position_bitget(SYMBOL)

        # ✅ If in position, place TPP using the ACTUAL entry price

        in_pos, side_detected, entry_price, qty, *_ = wait_for_position(SYMBOL)

        if in_pos:
            # 🎯 Pose du TPP (UNE SEULE FOIS après le trade)
            TRAIL_TRIGGER = float(TRAIL_TRIGGER)
            assert 0 < TRAIL_TRIGGER < 0.5, "❌ TRAIL_TRIGGER appears to be incorrectly set (not in %)"
            if USE_TPP:
                tpp_price = entry_price * (1 + TRAIL_TRIGGER) if side_detected.upper() == 'LONG' else entry_price * (1 - TRAIL_TRIGGER)
                tpp_qty = qty * PARTIAL_EXIT_FRACTION
                place_partial_tpp_visible(SYMBOL, side_detected.lower(), tpp_price, tpp_qty, MARGIN_MODE)

            # 🛡️ Pose initiale TP/SL
            tp_price = entry_price * (1 + TP_PERCENT_LONG / 100) if side_detected.upper() == 'LONG' else entry_price * (1 - TP_PERCENT_SHORT / 100)
            sl_price = entry_price * (1 - SL_PERCENT_LONG / 100) if side_detected.upper() == 'LONG' else entry_price * (1 + SL_PERCENT_SHORT / 100)
            tp_price = round(tp_price, PRICE_PRECISION)
            sl_price = round(sl_price, PRICE_PRECISION)
            set_full_tp_sl(SYMBOL, side_detected.lower(), tp_price, sl_price, demo=USE_DEMO, mode=MARGIN_MODE)

        else:
            print("❌ Error: Position not visible after opening.")
            
    while True:
        start_ts = time.time()
        try:
            if internet_alert_sent:
                try:
                    requests.get("https://api.bitget.com/api/v2/spot/public/coins", timeout=5)
                    if TELEGRAM_ENABLED:
                        send_telegram_message("✅ Internet connection restored, resuming Bitget bot.")
                    logging.info("✅ Internet connection restored.")

                    internet_was_down = False
                    internet_alert_sent = False
                    already_reported_internet_down = False
                    internet_ko_logged = False
                    retry_count = 0

                except Exception:
                    logging.warning("🌐 Internet confirmed down, waiting without making further API calls...")
                    time.sleep(RETRY_DELAY)
                    continue 
            # 2. Préparation des données
            df_hist = prepare_data()
            time.sleep(5)
            sig = check_signal_bb_rsi(df_hist)
            track_signal_activity(sig, in_pos)
            
            # 4. Détection de la position existante
            result = detect_current_position_bitget(SYMBOL)
            if result is None or len(result) != 7:
                raise ValueError("detect_current_position_bitget() did not return the expected result")
            
            in_pos, side, entry_price, qty, full_tp, full_sl, partial_tps = result
            if partial_tps is None:
                partial_tps = []
            # Nouvelle prise de position si signal détecté
            if sig in ['LONG', 'SHORT'] and not in_pos:
                print(f"📈 Signal detected ({sig}) — Entering position...")

                acc = send_signed_request('/api/v2/mix/account/accounts', 'GET', {'productType': 'USDT-FUTURES'})
                account_data = acc['data'][0]
                bal = float(account_data.get('available') or account_data.get('isolatedMaxAvailable'))

                set_margin_mode(SYMBOL, MARGIN_MODE)
                set_leverage(SYMBOL, LEVERAGE, MARGIN_MODE)

                price = df_hist['close'].iloc[-1]
                margin_amount = bal * CAPITAL_ENGAGEMENT
                size = margin_amount * LEVERAGE / price
                size = float(f"{size:.{QUANTITY_PRECISION}f}")

                side = 'buy' if sig == 'LONG' else 'sell'
                oid, resp = place_market_order(SYMBOL, size, side, MARGIN_MODE)
                
                in_pos, side_detected, entry_price, qty, *_ = wait_for_position(SYMBOL)

                if in_pos:
                    # 🎯 Pose du TPP (UNE SEULE FOIS après le trade)
                    TRAIL_TRIGGER = float(TRAIL_TRIGGER)
                    assert 0 < TRAIL_TRIGGER < 0.5, "❌ TRAIL_TRIGGER appears to be incorrectly set (not in %)"
                    if USE_TPP:
                        tpp_price = entry_price * (1 + TRAIL_TRIGGER) if side_detected.upper() == 'LONG' else entry_price * (1 - TRAIL_TRIGGER)
                        tpp_qty = qty * PARTIAL_EXIT_FRACTION
                        place_partial_tpp_visible(SYMBOL, side_detected.lower(), tpp_price, tpp_qty, MARGIN_MODE)

                    # 🛡️ Pose initiale TP/SL
                    tp_price = entry_price * (1 + TP_PERCENT_LONG / 100) if side_detected.upper() == 'LONG' else entry_price * (1 - TP_PERCENT_SHORT / 100)
                    sl_price = entry_price * (1 - SL_PERCENT_LONG / 100) if side_detected.upper() == 'LONG' else entry_price * (1 + SL_PERCENT_SHORT / 100)
                    tp_price = round(tp_price, PRICE_PRECISION)
                    sl_price = round(sl_price, PRICE_PRECISION)
                    set_full_tp_sl(SYMBOL, side_detected.lower(), tp_price, sl_price, demo=USE_DEMO, mode=MARGIN_MODE)
                    just_placed_tp_sl = True  # ⛔ Bloque la vérification au cycle suivant
                else:
                    print("❌ Error: Position not visible after opening.")
                time.sleep(0.3)


            # 🧱 Pose TP/SL/TPP SI en position
            if in_pos and not just_placed_tp_sl:
                if full_tp is None or full_sl is None:
                    print("📌 TP/SL not detected, placing (or replacing) them...")
                    tp_price = entry_price * (1 + TP_PERCENT_LONG/100) if side=='LONG' else entry_price * (1 - TP_PERCENT_SHORT/100)
                    sl_price = entry_price * (1 - SL_PERCENT_LONG/100) if side=='LONG' else entry_price * (1 + SL_PERCENT_SHORT/100)
                    tp_price = round(tp_price, PRICE_PRECISION)
                    sl_price = round(sl_price, PRICE_PRECISION)
                    set_full_tp_sl(SYMBOL, side.lower(), tp_price, sl_price, demo=USE_DEMO, mode=MARGIN_MODE)              
            # 🔁 Remise à zéro du flag                     
            just_placed_tp_sl = False

            # 📊 Dashboard
            print(f"⚙️  Leverage set : {LEVERAGE}x")
            info = fetch_dashboard_info(SYMBOL)
            print_dashboard(info, SYMBOL)

            # 🔄 Sortie totale
            if not in_pos and prev_qty:
                info = fetch_dashboard_info(SYMBOL)
                msg_telegram = (
                    f"📤 *Position Closed*\n"
                    f"📉 Current Price: `{info['mark_price']:.{PRICE_PRECISION}f}` USDT\n"
                    f"💰 *Capital*: `{info['equity']:.2f}` USDT"
                )

                msg_log = (
                    f"POSITION CLOSED: {info['mark_price']:.{PRICE_PRECISION}f} USDT | "
                    f"Capital: {info['equity']:.2f}"
                )

                if TELEGRAM_ENABLED:
                    send_telegram_message(msg_telegram)

                logging.info(msg_log)

                prev_qty = None
                partial_status = 'Waiting'
            else:
                if prev_qty is None:
                    partial_status = 'Waiting'
                elif qty < prev_qty:
                    partial_status = colorama.Fore.GREEN + 'executed' + colorama.Style.RESET_ALL
                    info = fetch_dashboard_info(SYMBOL)
                    msg = (
                        f"✅ *Partial exit executed*\n"
                        f"📉 Current price: `{info['mark_price']:.{PRICE_PRECISION}f}` USDT\n"
                        f"💰 Capital: `{info['equity']:.2f}` USDT\n"
                        f"📏 New position size: `{qty:.{QUANTITY_PRECISION}f}` {SYMBOL}"
                    )
                    if TELEGRAM_ENABLED:
                        send_telegram_message(msg)

                    logging.info(
                        f"PARTIAL EXIT executed at {info['mark_price']:.{PRICE_PRECISION}f} - remaining qty: {qty:.{QUANTITY_PRECISION}f} - Capital: {info['equity']:.{PRICE_PRECISION}f}"
                    )
                prev_qty = qty

            # 📋 Affichage
            if in_pos:
                print(f"📌 Position  : {side} | Entry : {entry_price:.{PRICE_PRECISION}f} | Qty : {qty:.{QUANTITY_PRECISION}f} {SYMBOL}")
                if full_tp:
                    print(f"🎯 TP active : {full_tp:.{PRICE_PRECISION}f}")
                if full_sl:
                    print(f"🛡️  SL active : {full_sl:.{PRICE_PRECISION}f}")
                if USE_TPP and partial_tps:
                    for p, q in partial_tps:
                        print(f"🏹 Active TPP : {p:.{PRICE_PRECISION}f} | Qty : {q:.{QUANTITY_PRECISION}f}")
                print(f"🔄 Partial exit status: {partial_status}")
            else:
                print_indicator_conditions(df_hist)
                

            print("=" * 50)
            print("✅ Cycle complete. Live price tracking during wait...\n")
            live_price_preview_simple(SYMBOL, interval_sec=2, total_duration_sec=LOOP_INTERVAL)
            print(" " * 50)

            # Nettoyage console
            cycle_count += 1
            if cycle_count % CYCLE_COUNT == 0:
                clear_console()
                print(Fore.GREEN + "♻️ Console automatically cleared.\n" + Style.RESET_ALL)

            # Vérif Internet rapide
            try:
                requests.get("https://api.bitget.com/api/v2/spot/public/coins", timeout=5)
            except Exception:
                raise ConnectionError("Bitget check error – possible internet loss")

        except (ConnectionError, requests.exceptions.ConnectionError, ccxt.NetworkError) as e:
            retry_count += 1
            internet_was_down = True

            if retry_count == 1 and not already_reported_internet_down:
                logging.warning(f"🌐 Network error: attempting to reconnect...")
                already_reported_internet_down = True

            logging.warning(f"🌐 Erreur réseau dans prepare_data() ({retry_count}/{MAX_RETRIES}) : {e}")

            if retry_count >= MAX_RETRIES:
                if TELEGRAM_ENABLED and not internet_alert_sent:
                    try:
                        send_telegram_message("🚨 Bitget Bot: Internet has been unavailable for several minutes!")
                    except Exception as e:
                        logging.warning(f"Erreur Telegram : {e}")
                    logging.error("🌐 Internet still down after multiple attempts.")
                    internet_alert_sent = True

            time.sleep(RETRY_DELAY)
            continue

        except KeyboardInterrupt:
            print("🛑 Manual bot shutdown.")
            break

#######################################################################################

    # ───────────── LIVE MODE CONFIGURATION ─────────────
    # To switch to mainnet (live trading):
    #  • Set USE_DEMO = False
    #  • Replace 'SUSDT-FUTURES' → 'USDT-FUTURES' in API calls
    #  • Disable TEST_MODE or set it to False

# - In all your functions where you define:
# product_type = 'SUSDT‑FUTURES' if demo else 'USDT‑FUTURES'

# – To stay in demo mode, keep demo=True, you'll use:
# "productType": "SUSDT‑FUTURES"

# – To switch to live mode, set demo=False (and remove the header paptrading=1), and you'll use:
# "productType": "USDT‑FUTURES"

# - If you trade Coin-M futures live, use:
# "productType": "COIN‑FUTURES"

# And for demo mode with Coin-M futures:
# "productType": "SCOIN‑FUTURES"

# Quick summary:
# Mode     USDT‑M Futures     Coin‑M Futures
# Demo     SUSDT‑FUTURES      SCOIN‑FUTURES
# Live     USDT‑FUTURES       COIN‑FUTURES
