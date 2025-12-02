"""
Vinted Scraper - Script principal
Scrape les annonces Vinted et envoie des notifications Discord pour les nouveautés
"""

import time
import json
from datetime import datetime
from utils import build_vinted_url, scrape_vinted_page, extract_item_id
from discord_webhook import send_discord_embed

# Configuration
SCAN_INTERVAL = 60  # Secondes entre chaque scan
SEARCHES_FILE = "searches.json"

# Stockage en mémoire des IDs déjà vus
seen_items = set()


def load_searches():
    """Charge les recherches depuis le fichier JSON"""
    try:
        with open(SEARCHES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('searches', [])
    except FileNotFoundError:
        print(f"❌ Fichier {SEARCHES_FILE} introuvable")
        return []
    except json.JSONDecodeError:
        print(f"❌ Erreur de format dans {SEARCHES_FILE}")
        return []


def process_search(search_config):
    """
    Traite une recherche spécifique
    
    Args:
        search_config: Dictionnaire contenant les paramètres de recherche
    """
    search_name = search_config.get('name', 'Sans nom')
    webhook_url = search_config.get('webhook_url')
    
    if not webhook_url:
        print(f"⚠️  Pas de webhook pour '{search_name}', ignoré")
        return
    
    print(f"\n🔍 Analyse: {search_name}")
    
    # Construction de l'URL Vinted
    url = build_vinted_url(search_config)
    print(f"📡 URL: {url[:80]}...")
    
    # Scraping de la page
    items = scrape_vinted_page(url)
    
    if items is None:
        print(f"❌ Échec du scraping pour '{search_name}'")
        return
    
    print(f"📦 {len(items)} articles trouvés")
    
    # Détection des nouveautés
    new_items = []
    for item in items:
        item_id = extract_item_id(item.get('url', ''))
        if item_id and item_id not in seen_items:
            seen_items.add(item_id)
            new_items.append(item)
    
    # Envoi des notifications Discord
    if new_items:
        print(f"🆕 {len(new_items)} nouveaux articles détectés!")
        for item in new_items:
            success = send_discord_embed(webhook_url, item, search_name)
            if success:
                print(f"✅ Envoyé: {item.get('title', 'Sans titre')[:50]}")
            else:
                print(f"❌ Échec envoi: {item.get('title', 'Sans titre')[:50]}")
            time.sleep(1)  # Pause pour éviter le rate limiting Discord
    else:
        print("💤 Aucun nouvel article")


def main():
    """Fonction principale - Boucle infinie de scraping"""
    print("=" * 60)
    print("🚀 VINTED SCRAPER - Démarrage")
    print("=" * 60)
    print(f"⏱️  Intervalle de scan: {SCAN_INTERVAL} secondes")
    print(f"📄 Fichier de recherches: {SEARCHES_FILE}")
    print("=" * 60)
    
    # Chargement initial des recherches
    searches = load_searches()
    
    if not searches:
        print("❌ Aucune recherche configurée. Arrêt du programme.")
        return
    
    print(f"✅ {len(searches)} recherche(s) chargée(s)")
    
    # Boucle principale
    scan_count = 0
    try:
        while True:
            scan_count += 1
            print(f"\n{'=' * 60}")
            print(f"🔄 SCAN #{scan_count} - {datetime.now().strftime('%H:%M:%S')}")
            print(f"{'=' * 60}")
            
            # Rechargement des recherches à chaque cycle
            searches = load_searches()
            
            # Traitement de chaque recherche
            for idx, search in enumerate(searches, 1):
                print(f"\n[{idx}/{len(searches)}]", end=" ")
                process_search(search)
                time.sleep(2)  # Pause entre chaque recherche
            
            print(f"\n💤 Attente de {SCAN_INTERVAL} secondes...")
            time.sleep(SCAN_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Arrêt du scraper demandé par l'utilisateur")
        print(f"📊 Total de scans effectués: {scan_count}")
        print(f"📦 Total d'articles mémorisés: {len(seen_items)}")
        print("\n👋 Au revoir!")


if __name__ == "__main__":
    main()
