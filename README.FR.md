# 🤖 Bitget Trading Bot V8.8
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Actively--Maintained-brightgreen)
![Bot](https://img.shields.io/badge/Type-Trading%20Bot-blueviolet)
![QA Ready](https://img.shields.io/badge/QA--Friendly-Yes-success)

## ⚠️Utilisé à ses propres risques⚠️
> 🇬🇧 Read in English: [README.md](README.md)

Bot de trading automatisé pour la plateforme **Bitget**, écrit en **Python**.  
Il utilise une stratégie combinée **Bollinger Bands + RSI**, avec gestion intelligente du **Take Profit**, **Stop Loss** et **TP partiel**.  
Le bot peut s’exécuter en **mode test/démo** ou **réel**, avec notifications **Telegram**.

---

## ⚠️ Prérequis & Compatibilité

- Un compte [Bitget](https://www.bitget.com/)
- Ce bot est conçu pour le **trading sur contrats Futures uniquement** (pas Spot).
- Il fonctionne uniquement avec des **paires en USDT**, comme `BTCUSDT`, `ETHUSDT`, etc.
- Nécessite un compte Bitget avec des clés API Futures (en mode démo ou réel).
- Python 3.9 ou version supérieure recommandé.

## 🚀 Fonctionnalités principales

- 📈 Détection de signaux : stratégie Bollinger + RSI + filtre de volatilité
- 🤖 Prise de position automatique (LONG / SHORT)
- 🧠 TP / SL posés dès la confirmation d'ouverture
- 🏹 Take Profit Partiel (TPP) configurable
- 📊 Dashboard complet en live (prix, equity, position…)
- 🔁 Boucle principale avec vérifications, logs et affichage dynamique
- 🌐 Gestion intelligente des coupures réseau (et reprise automatique)
- 🛠️ Intégration Telegram (alertes et notifications en temps réel)
- 🧪 Mode TEST intégré pour simuler un trade sans attendre de signal

## 🧱 Architecture du bot

Le bot est organisé autour de modules robustes :

- **Analyse de marché** : récupération des bougies avec CCXT + calcul Bollinger/RSI
- **Détection de signal** : stratégie personnalisable (`check_signal_bb_rsi`)
```
==================================================
✅ RSI faible : 25,71 < 60
📏 Bande supérieure : 2 698,01, Bande inférieure : 2 647,63, MMS : 2 672,82
⚠️ Faible volatilité : largeur 0,0189 ≤ seuil 0,0270
➡️ Prix entre les bandes : 2 661,57
👀 En attente du prochain signal…
==================================================
```
- **Exécution des ordres** : market order + gestion du mode marge et levier
- **Protection des positions** : TP/SL automatiques, TPP (Take Profit Partiel)
- **Surveillance continue** : dashboard en direct, affichage console dynamique
```
 ⚙️  Levier réglé : 3x
 ================== Version 8.8 ==================
 📅 2025-05-27 21:03:49 | Prix ETHUSDT : 2676.00 USDT
 🏦 Total capital       : 5109.23 USDT
 💰 Solde en USDT       : 5222.44 USDT
 💸 disponible          : 138.73 USDT
 ⚖️ P&L non réalisé    : 113.21 USDT
 📏 Initial Margin      : 4970.50 USDT
 📊 Initial Margin %    : 97.28 %
 ==================================================
 📌 Position  : SHORT | Entrée : 2696.47 | Qté : 5.53 ETHUSDT
 🎯 TP actif  : 2669.51
 🛡️ SL actif  : 2736.92
 🔄 Sortie partielle : en attente
 ```
- **Communication** : notifications Telegram, logs locaux

![Notifications Telegram](./assets/telegram-demo.png/)
---

## 🧩 Stratégie personnalisable

Le bot repose par défaut sur une stratégie technique éprouvée combinant trois outils :

🔷 **1. Bandes de Bollinger (Bollinger Bands)**
- Permettent de visualiser les zones de **surachat/survente** en fonction de la volatilité.
- Le bot détecte les **cassures** de bande (breakouts), ce qui peut signaler une entrée potentielle.

🔶 **2. RSI (Relative Strength Index)**
- Utilisé pour **filtrer les faux signaux**.
- Le RSI doit confirmer la dynamique :
- 📈 Pour un **LONG**, on attend que le RSI dépasse un seuil (ex. > 40).
- 📉 Pour un **SHORT**, on attend qu’il passe sous un seuil (ex. < 60).

♦️ **3. Filtre de volatilité (propre au bot)**
- Calcul basé sur la **largeur des bandes de Bollinger**.
- Le trade est autorisée uniquement si la volatilité est suffisante, pour éviter les marchés plats.


Mais il est **conçu pour être facilement modifiable** :  
➡️ Vous pouvez adapter **votre propre stratégie de trading**, sans toucher au cœur du bot.

## 🔁 Comment faire ?

Dans le fichier `BitgetBotV8.8.py`, la fonction suivante détermine les signaux :

```python
def check_signal_bb_rsi(df):
    ...
    return "LONG", "SHORT", ou None

```

## 📦 Installation
```
git clone https://github.com/jerome78b/bitget-trading-bot.git
```
```
cd bitget-trading-bot
```
```
python -m venv venv
```
```
pip install -r requirements.txt
```
---

## 🛠️ Configuration & Variables

Vous pouvez personnaliser le bot en modifiant les variables situées en haut du fichier `BitgetBot.py`.

Voici les principales variables de configuration et leur rôle :

| Variable        | Type   | Description                                                                 |
|-----------------|--------|-----------------------------------------------------------------------------|
| `USE_DEMO`      | `bool` | `True` = utilise l’environnement démo de Bitget (testnet), `False` = trading réel |
| `TEST_MODE`     | `bool` | `True` = force un trade simulé à chaque exécution, `False` = active la stratégie réelle (BB + RSI) |
| `TEST_SIDE`     | `str`  | Si `TEST_MODE = True`, permet de choisir `'buy'` ou `'sell'` pour le test      |
| `USE_TPP`       | `bool` | `True` = active le Take Profit Partiel (TPP), `False` = le désactive entièrement |
| `SYMBOL`        | `str`  | Paire en USDT à trader, ex : `'ETHUSDT'`, `'SOLUSDT'`                          |
| `TIMEFRAME`     | `str`  | Période des bougies utilisées, ex : `'1m'`, `'5m'`, `'15m'`, `'1h'`            |
| `LEVERAGE`      | `int`  | Levier appliqué à la position (ex : `3`, `5`, `10`)                           |
| `CAPITAL_ENGAGEMENT`      | `float`  |Pourcentage du capital à allouer (10%) (ex :`0.10`)                   |

## ✏️ Configuration
```
API_KEY=your_api_key
API_SECRET=your_api_secret
PASSPHRASE=your_passphrase
TELEGRAM_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_chat_id
```
---

## ❓ Pourquoi utiliser ce bot ?

Ce projet a été conçu pour rendre le **trading automatisé sur Bitget simple, modulable et prêt à l’emploi**, notamment pour les débutants ou les profils QA/développeurs qui souhaitent :

- ✅ Un exemple fonctionnel complet d’intégration avec l’API Bitget
- 🧠 Un système de stratégie personnalisable (remplacez facilement la logique)
- 🧪 Un mode TEST intégré pour simuler des trades sans risque
- 💬 Des alertes en temps réel via Telegram
- 📊 Un tableau de bord clair avec les prix, l’équity et l’état des positions
- 🔐 Une gestion robuste des erreurs (déconnexions Internet, erreurs API...)

Au lieu de partir de zéro avec les SDK ou l’API brute, ce bot vous permet de **vous concentrer sur votre stratégie**, pas sur la configuration technique.

Idéal pour :
- 👨‍💻 Les développeurs qui veulent une base propre orientée QA
- 📈 Les traders qui veulent automatiser leurs entrées RSI + Bollinger
- 🧪 Ceux qui apprennent à construire ou tester une stratégie crypto automatisée

---

## 📄 Licence
Ce projet est sous licence MIT – libre d’utilisation, modification et distribution.

## ⭐ Soutenir le projet

Si ce bot vous a été utile ou vous semble intéressant, vous pouvez lui donner une **⭐ étoile** sur GitHub !

Cela m’aide à gagner en visibilité, à rester motivé, et à faire évoluer ce projet open-source.

➡️ [Ajouter une étoile ici](https://github.com/jerome78b/bitget-trading-bot/stargazers) 🙏

## 🙋‍♂️ À propos

Ce projet a été développé dans le cadre d'une démonstration de compétences en **tests QA**, **développement Python** et **automatisation**.  
N'hésitez pas à me contacter si vous êtes recruteur ou intéressé par un projet technique.

📬 **Me contacter** :  
[![GitHub](https://img.shields.io/badge/GitHub-jerome78b-181717?logo=github)](https://github.com/jerome78b)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-jerome--profil-blue?logo=linkedin)](https://www.linkedin.com/in/jerome-bauché)
