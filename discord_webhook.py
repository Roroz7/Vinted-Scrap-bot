"""
Module d'envoi de notifications Discord via Webhook
"""

import requests
from datetime import datetime


def send_discord_embed(webhook_url, item, search_name):
    """
    Envoie un embed Discord avec les informations d'un article
    
    Args:
        webhook_url: URL du webhook Discord
        item: Dictionnaire contenant les infos de l'article
        search_name: Nom de la recherche
        
    Returns:
        bool: True si envoi réussi, False sinon
    """
    
    # Construction de l'embed
    embed = {
        "title": item.get('title', 'Article Vinted')[:256],  # Limite Discord: 256 caractères
        "url": item.get('url', ''),
        "color": 0x09B1BA,  # Couleur Vinted (bleu-vert)
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {
            "text": f"Recherche: {search_name}"
        },
        "thumbnail": {
            "url": item.get('image', '')
        },
        "fields": []
    }
    
    # Ajout des champs
    if item.get('price'):
        embed['fields'].append({
            "name": "💰 Prix",
            "value": item.get('price'),
            "inline": True
        })
    
    if item.get('size') and item.get('size') != 'Non spécifié':
        embed['fields'].append({
            "name": "📏 Taille",
            "value": item.get('size'),
            "inline": True
        })
    
    if item.get('brand') and item.get('brand') != 'Inconnue':
        embed['fields'].append({
            "name": "🏷️ Marque",
            "value": item.get('brand'),
            "inline": True
        })
    
    if item.get('condition') and item.get('condition') != 'Non spécifié':
        embed['fields'].append({
            "name": "✨ État",
            "value": item.get('condition'),
            "inline": True
        })
    
    # Payload complet
    payload = {
        "username": "Vinted Scraper",
        "avatar_url": "https://images.vinted.net/assets/icon-192x192.png",
        "embeds": [embed]
    }
    
    # Envoi du webhook
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 204:
            return True
        elif response.status_code == 429:
            print("⚠️  Rate limit Discord atteint, ralentissement nécessaire")
            return False
        else:
            print(f"⚠️  Code retour Discord: {response.status_code}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Erreur webhook Discord: {e}")
        return False
