
## [V8.8] - 2025-05-27
🖥️ **Affichage visuel des conditions sans signal**
- Ajout de la fonction print_indicator_conditions() :
- Affichage coloré du RSI (haut, bas, neutre) avec ✅/🔒/⚠️
- Détail des bandes de Bollinger (SMA, upper, lower) et de la volatilité (width vs seuil)
- Indication du positionnement du prix par rapport aux bandes (🔼/🔽/➡️)

---

## [V8.7] - 2025-05-02
🧩 **Option d’activation TPP**
- Ajout de la variable globale USE_TPP = True en haut du script.
- Permet de désactiver totalement le Take Profit Partiel (TPP) avec USE_TPP = False
- Le TPP (via place_partial_tpp_visible) ne sera ni posé ni affiché si désactivé.
- Nettoyage de l'affichage 🏹 TPP actif conditionné à USE_TPP.
- 🔒 Sécurité conservée : le TP/SL principal reste toujours actif même si USE_TPP = False.

---

## [V8.6] - 2025-04-27
✨ **Gestion des précisions symboles**
- Ajout d'une détection manuelle par SYMBOL.startswith() pour définir PRICE_PRECISION et QUANTITY_PRECISION.
- Suppression de l'appel CCXT automatique pour plus de stabilité.
🛠 **Correction du formatage dynamique**
- Fix du formattage float(f"{size:.{QUANTITY_PRECISION}f}") avec conversion int() sur la précision6
🚀 **Optimisations**
- Nettoyage du démarrage : affichage clair du SYMBOL utilisé.
- Robustesse accrue sur la gestion réseau et sur les erreurs TP/SL.

---

## [V8.5] - 2025-04-26
📈 **Fix analyse signaux**
- Modification du calcul du signal Bollinger+RSI : 
- Analyse désormais sur la **bougie précédente** (`df.iloc[-2]`) au lieu de la bougie en cours (`df.iloc[-1]`)
- Cela évite les faux signaux prématurés avant la clôture.
- Correction également de la fonction `check_signal(df)` (utilise maintenant la bougie précédente).
- Ajout d'un `time.sleep(5)` après le chargement des données ➔ pour garantir que la bougie est bien clôturée et synchro avec l'API Bitget.
🧪 **Tests de robustesse validés**
- Simulations de signaux ➔ prise de position uniquement sur bougie clôturée.
- Confirmé : plus aucun trade déclenché au milieu d'une bougie (ex: 15h42 ou 16h07).

---

## [V8.4] - 2025-04-24
🌐 **Gestion réseau intelligente**
- Ajout d'une vraie détection de coupure Internet ➔ compteur 1/10, 2/10, 3/10
- Blocage automatique des logs `"Internet toujours KO après plusieurs essais"` pour éviter le spam
- Détection propre de la reconnexion Internet avec envoi automatique sur Telegram
- Réinitialisation complète des flags (`retry_count`, `internet_was_down`, `already_reported_internet_down`) à la reconnexion
🛡️ **Protection contre flood de logs**
- Nettoyage intelligent de la console et des fichiers de log pendant les coupures
- Limite stricte sur les erreurs affichées : une seule erreur réseau affichée par cycle critique
⚡ **Optimisation cycle principal**
- Correction de la gestion du `retry_count` pour permettre plusieurs détections de coupure sans bug
- Pause dynamique de 30 secondes entre les tentatives en cas de réseau indisponible
- Reprise du cycle normal sans besoin de redémarrer le bot après une coupure
📈 **Tests de robustesse validés**
- Coupures Internet simulées ➔ reprise OK
- Logs propres, sans doublon
- Notification Telegram 100% fiable après reconnexion

---

## [V8.3] - 2025-04-23
🔧 **Fix TP/SL Bitget**
- Ajout du champ delegateType pour éviter l’erreur delegateType is error
- Pose des TP/SL désormais sans erreur, logs nettoyés

---

## [V8.2] - 2025-04-23 
🚀 **Sécurisation post-trade (TPP + SL/TP)**
- Ajout de la fonction `wait_for_position()` ➜ attente active jusqu’à détection réelle de la position ouverte
- Pose du TPP (Take Profit Partiel) **immédiatement après le trade**, une seule fois
- Pose directe du TP/SL dès confirmation de position (plus d’erreur `delegateType is error`)
- `TEST_MODE` amélioré ➜ un seul trade lancé au démarrage, plus de spam dans la boucle
- Refactor du `__main__` ➜ logique identique à la boucle : détection signal, prise de position, TPP, TP/SL
- Arrondi sécurisé des prix TP/SL avec `round(..., 2)` pour éviter tout rejet de l’API Bitget
🧪 **Tests & vérifs**
- Test rapide via `TEST_MODE = True` validé (LONG ou SHORT)
- Logs clairs : position détectée ➜ TPP posé ➜ SL/TP posés
- Structure prête pour retour en mode stratégie (TEST_MODE = False)

---

## [V8.1] - 2025-04-22 soir
🧠 **Migration complète vers bougies Futures via CCXT**
- Intégration de la récupération d’historique en CCXT (fetch_ohlcv) pour contrats Futures
- Création de la `variable SYMBOL_CCXT` automatiquement dérivée de SYMBOL (format ETH/USDT:USDT)
- Refactor de la fonction fetch_historical() pour utiliser CCXT de façon propre
- Utilisation de SYMBOL_CCXT dans la fonction prepare_data()
- Support direct du changement de SYMBOL et TIMEFRAME sans modifier le code
- Validation automatique du format des symboles pour éviter les erreurs CCXT
- 🧼 Refactor de la configuration
- Conversion automatique du symbole vers le format compatible Futures CCXT
- Suppression des redéfinitions de variables inutiles dans le corps du script
🧪 **Tests & vérifs**
- Vérification du retour de df.iloc[-1] pour obtenir la dernière bougie à jour (ex : 23:30)
- Confirmation que les données CCXT sont bien live et synchronisées
- Nettoyage des blocs inutiles liés au testnet ou aux appels natifs bloqués
- 🐛 Bug corrigé `(hérité de la V8)` :
- Correction d’un TypeError lors du calcul de tp_price (bug causé par entry qui contenait un dict)

---

## [V8] - 2025-04-22
🛠️ **Refonte complète des logs & erreurs**
- Refactor des logs : format 1 ligne, suppression des doublons
- Système `send_error_once()` : envoie 1 seule fois une erreur (log + Telegram)
- Anti-spam pour toutes les erreurs (TP, SL, TPP, boucle, etc.)
- Regroupement propre des erreurs TP/SL sur 1 ligne
- Amélioration `place_partial_tpp_visible` avec log+Telegram intégré
- Récupération du prix réel via `detect_current_position_bitget`
- Nettoyage des erreurs dans la boucle principale (traceback Telegram)
- Logging et Telegram optimisés pour le TPP

---

## [V7] - 2025-04-21
📈 **Amélioration des cycles et stratégie**
- Affichage du prix ETH en live avec variation à chaque cycle
- Ajout complet des logs et intégration Telegram
- Intégration de la stratégie Bollinger + RSI (vérification des indicateurs)
- Nettoyage automatique du terminal toutes les X bougies

---

## [V6] - 2025-04-18
🎯 **Amélioration TPP & surveillance automatique**
- TPP (Take Profit Partiel) placé uniquement à l’ouverture d’un trade
- SL/TP repositionnés automatiquement si manquants à chaque cycle
- Logique plus robuste sur la surveillance des ordres actifs

---

## [V5] - 2025-04-15
🔁 **Création de la boucle principale**
- Implémentation du cœur du bot (loop/cycle de vérification)
- Affichage complet du dashboard (prix, equity, position, etc.)
- Ajout de la sortie partielle avec statut affiché (exécutée / en attente)

---

## [V4] - 2025-04-13
💰 **Gestion de position active**
- Mise en place du TP partiel (fonctionnelle)
- Vérification de position existante avant de lancer un nouveau trade

---

## [V3] - 2025-04-10
🎯 **SL/TP et taille auto**
- Arrondi auto de la taille de position à 2 décimales
- Ajout de la gestion des TP (Take Profit) et SL (Stop Loss)

---

## [V2] - 2025-04-07
⚙️ **Fondations techniques**
- Mise en place du levier dynamique
- Ajout du support des positions LONG et SHORT
- Mise à jour complète de la gestion du levier et du mode de marge
