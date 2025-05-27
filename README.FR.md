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

---

## 🧩 Stratégie personnalisable

Le bot utilise par défaut une stratégie basée sur :

- **Bandes de Bollinger**
- **RSI (Relative Strength Index)**
- Un filtre de **volatilité** basé sur la largeur des bandes

Mais il est **conçu pour être facilement modifiable** :  
➡️ Vous pouvez adapter **votre propre stratégie de trading**, sans toucher au cœur du bot.

## 🔁 Comment faire ?

Dans le fichier `BitgetBotV8.7.py`, la fonction suivante détermine les signaux :

```python
def check_signal_bb_rsi(df):
    ...
    return "LONG", "SHORT", ou None

```

## 📦 Installation
```
git clone https://github.com/jerome78b/bitget-trading-bot.git
cd bitget-trading-bot
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
