"""
Fonctions utilitaires pour le scraping Vinted
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode

# Headers pour simuler un navigateur réel
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}


def build_vinted_url(search_config):
    """
    Construit l'URL de recherche Vinted à partir de la configuration
    
    Args:
        search_config: Dictionnaire avec les paramètres de recherche
        
    Returns:
        str: URL complète de recherche Vinted
    """
    base_url = "https://www.vinted.fr/catalog"
    params = {}
    
    # Mots-clés
    if search_config.get('keywords'):
        params['search_text'] = search_config['keywords']
    
    # Prix
    if search_config.get('price_from'):
        params['price_from'] = search_config['price_from']
    if search_config.get('price_to'):
        params['price_to'] = search_config['price_to']
    
    # Tailles (format: size_ids[]=206&size_ids[]=207)
    if search_config.get('sizes'):
        for size in search_config['sizes']:
            params.setdefault('size_ids[]', []).append(size) if isinstance(params.get('size_ids[]'), list) else params.update({'size_ids[]': size})
    
    # État (1=Neuf avec étiquette, 2=Neuf sans étiquette, 3=Très bon état, 4=Bon état, 5=Satisfaisant)
    if search_config.get('status'):
        for status in search_config['status']:
            params.setdefault('status_ids[]', []).append(status) if isinstance(params.get('status_ids[]'), list) else params.update({'status_ids[]': status})
    
    # Catégorie
    if search_config.get('catalog'):
        params['catalog[]'] = search_config['catalog']
    
    # Tri (newest_first, price_low_to_high, price_high_to_low, relevance)
    if search_config.get('order'):
        params['order'] = search_config['order']
    
    # Construction de l'URL
    if params:
        # Gestion spéciale pour les paramètres array
        url_parts = []
        for key, value in params.items():
            if isinstance(value, list):
                for v in value:
                    url_parts.append(f"{key}={v}")
            else:
                url_parts.append(f"{key}={value}")
        query_string = "&".join(url_parts)
        return f"{base_url}?{query_string}"
    
    return base_url


def scrape_vinted_page(url):
    """
    Scrape une page Vinted et extrait les informations des articles
    
    Args:
        url: URL de la page à scraper
        
    Returns:
        list: Liste de dictionnaires contenant les infos des articles, ou None en cas d'erreur
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Recherche des articles dans le HTML
        # Vinted utilise des divs avec data-testid ou des classes spécifiques
        items = []
        
        # Méthode 1: Recherche par script JSON-LD (méthode la plus fiable)
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get('@type') == 'ItemList':
                    for item in data.get('itemListElement', []):
                        product = item.get('item', {})
                        items.append({
                            'title': product.get('name', 'Sans titre'),
                            'price': extract_price(product.get('offers', {}).get('price', '0')),
                            'url': product.get('url', ''),
                            'image': product.get('image', ''),
                            'brand': product.get('brand', {}).get('name', 'Inconnue') if isinstance(product.get('brand'), dict) else 'Inconnue',
                            'condition': 'Non spécifié',
                            'size': 'Non spécifié',
                            'date': 'Maintenant'
                        })
            except:
                continue
        
        # Méthode 2: Parsing HTML classique si JSON-LD échoue
        if not items:
            article_divs = soup.find_all('div', class_=re.compile(r'feed-grid__item|new-item-box'))
            
            for div in article_divs:
                try:
                    # Extraction du lien
                    link_tag = div.find('a', href=re.compile(r'/items/'))
                    if not link_tag:
                        continue
                    
                    url_item = 'https://www.vinted.fr' + link_tag.get('href', '')
                    
                    # Extraction du titre
                    title = link_tag.get('title', '') or 'Sans titre'
                    
                    # Extraction du prix
                    price_tag = div.find('span', class_=re.compile(r'price|Text_text'))
                    price = price_tag.get_text(strip=True) if price_tag else '0 €'
                    
                    # Extraction de l'image
                    img_tag = div.find('img')
                    image = img_tag.get('src', '') if img_tag else ''
                    
                    items.append({
                        'title': title,
                        'price': price,
                        'url': url_item,
                        'image': image,
                        'brand': 'Inconnue',
                        'condition': 'Non spécifié',
                        'size': 'Non spécifié',
                        'date': 'Maintenant'
                    })
                except Exception as e:
                    continue
        
        return items[:30]  # Limite à 30 articles max
        
    except requests.RequestException as e:
        print(f"❌ Erreur réseau: {e}")
        return None
    except Exception as e:
        print(f"❌ Erreur de parsing: {e}")
        return None


def extract_price(price_str):
    """
    Extrait et formate le prix
    
    Args:
        price_str: Chaîne contenant le prix
        
    Returns:
        str: Prix formaté
    """
    if isinstance(price_str, (int, float)):
        return f"{price_str} €"
    
    # Extraction des chiffres
    match = re.search(r'(\d+[,.]?\d*)', str(price_str))
    if match:
        return f"{match.group(1)} €"
    return "0 €"


def extract_item_id(url):
    """
    Extrait l'ID unique d'un article depuis son URL
    
    Args:
        url: URL de l'article Vinted
        
    Returns:
        str: ID de l'article, ou None
    """
    match = re.search(r'/items/(\d+)', url)
    return match.group(1) if match else None
