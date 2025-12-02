# 🛍️ Vinted Scraper - Moniteur d'annonces en temps réel

Un scraper Python simple et efficace qui surveille les nouvelles annonces Vinted et vous notifie via Discord.

## 📋 Prérequis

- Python 3.7 ou supérieur
- Un webhook Discord (voir section Configuration)

## 🚀 Installation

### 1. Cloner ou télécharger le projet

```bash
git clone <votre-repo>
cd vinted_scraper
```

### 2. Installer les dépendances

```bash
pip install requests beautifulsoup4
```

Ou avec un fichier requirements.txt :

```bash
pip install -r requirements.txt
```

**Contenu de requirements.txt :**
```
requests>=2.31.0
beautifulsoup4>=4.12.0
```

## ⚙️ Configuration

### 1. Créer un Webhook Discord

1. Ouvrez Discord et allez dans les paramètres du salon souhaité
2. Cliquez sur **Intégrations** → **Webhooks**
3. Cliquez sur **Nouveau Webhook**
4. Copiez l'URL du webhook

### 2. Configurer vos recherches

Éditez le fichier `searches.json` :

```json
{
  "searches": [
    {
      "name": "Ma recherche",
      "webhook_url": "https://discord.com/api/webhooks/VOTRE_WEBHOOK_ICI",
      "keywords": "nike air max",
      "sizes": [207, 208],
      "price_from": 20,
      "price_to": 100,
      "status": [3, 4],
      "order": "newest_first"
    }
  ]
}
```

### 3. Paramètres disponibles

| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `name` | string | Nom de la recherche | `"Nike Air Max 90"` |
| `webhook_url` | string | **OBLIGATOIRE** URL du webhook Discord | `"https://discord.com/..."` |
| `keywords` | string | Mots-clés de recherche | `"nike air max"` |
| `sizes` | array | IDs des tailles Vinted | `[207, 208]` |
| `price_from` | number | Prix minimum | `20` |
| `price_to` | number | Prix maximum | `100` |
| `status` | array | États des articles (1-5) | `[3, 4]` |
| `catalog` | array | IDs des catégories | `["1193"]` |
| `order` | string | Tri des résultats | `"newest_first"` |

### États des articles (`status`)

- **1** : Neuf avec étiquette
- **2** : Neuf sans étiquette
- **3** : Très bon état
- **4** : Bon état
- **5** : Satisfaisant

### Ordre de tri (`order`)

- `newest_first` : Plus récents d'abord
- `price_low_to_high` : Prix croissant
- `price_high_to_low` : Prix décroissant
- `relevance` : Pertinence

### Trouver les IDs de tailles et catégories

1. Allez sur [vinted.fr](https://www.vinted.fr)
2. Faites une recherche avec les filtres souhaités
3. Regardez l'URL dans votre navigateur :
   ```
   https://www.vinted.fr/catalog?search_text=nike&size_ids[]=207&catalog[]=1193
   ```
4. Les IDs sont visibles dans l'URL (`207` pour la taille, `1193` pour la catégorie)

## 🏃 Lancement

### Démarrage simple

```bash
python scraper.py
```

### Configuration de l'intervalle de scan

Modifiez la variable `SCAN_INTERVAL` dans `scraper.py` :

```python
SCAN_INTERVAL = 60  # Scan toutes les 60 secondes
```

### Arrêter le scraper

Appuyez sur `Ctrl+C` dans le terminal

## 📁 Structure du projet

```
vinted_scraper/
├── scraper.py           # Script principal
├── utils.py             # Fonctions de scraping
├── discord_webhook.py   # Envoi des notifications Discord
├── searches.json        # Configuration des recherches
└── README.md           # Ce fichier
```

## 🔧 Fonctionnement

1. **Chargement** : Le script charge les recherches depuis `searches.json`
2. **Scraping** : Pour chaque recherche, il récupère les annonces Vinted
3. **Détection** : Il compare avec les IDs déjà vus (en mémoire)
4. **Notification** : Les nouveaux articles déclenchent un embed Discord
5. **Boucle** : Le processus se répète toutes les X secondes

## 📊 Exemple de sortie

```
============================================================
🚀 VINTED SCRAPER - Démarrage
============================================================
⏱️  Intervalle de scan: 60 secondes
📄 Fichier de recherches: searches.json
============================================================
✅ 2 recherche(s) chargée(s)

============================================================
🔄 SCAN #1 - 14:32:15
============================================================

[1/2] 
🔍 Analyse: Nike Air Max 90 - Taille 42
📡 URL: https://www.vinted.fr/catalog?search_text=nike+air+max+90...
📦 12 articles trouvés
🆕 3 nouveaux articles détectés!
✅ Envoyé: Nike Air Max 90 OG White Blue
✅ Envoyé: Air Max 90 Essential Black
✅ Envoyé: Nike Air Max 90 Leather Blanc

💤 Attente de 60 secondes...
```

## 🐛 Dépannage

### "Aucune recherche configurée"
- Vérifiez que `searches.json` existe et est valide
- Vérifiez que le tableau `searches` contient au moins une recherche

### "Pas de webhook pour X"
- Ajoutez le paramètre `webhook_url` à votre recherche dans `searches.json`

### "Échec du scraping"
- Vinted peut avoir changé sa structure HTML
- Vérifiez votre connexion Internet
- Essayez d'augmenter le délai entre les scans

### Notifications Discord non reçues
- Vérifiez que l'URL du webhook est correcte
- Vérifiez les permissions du webhook Discord
- Attention au rate limiting (max 30 messages par minute)

## ⚠️ Avertissements

- **Respect des CGU** : Utilisez ce scraper de manière responsable
- **Rate limiting** : Ne mettez pas un intervalle trop court (minimum 30-60 secondes recommandé)
- **Fiabilité** : Vinted peut modifier son site, le scraper devra être adapté
- **Usage personnel** : Ce projet est à but éducatif

## 📝 Licence

Projet à usage éducatif. Utilisez-le de manière responsable.

## 🤝 Contribution

N'hésitez pas à améliorer le code et partager vos modifications !

## 📧 Support

Pour toute question, ouvrez une issue sur le dépôt GitHub.

---

**Bon scraping ! 🚀**
