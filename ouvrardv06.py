import requests
from google.cloud import storage
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import pandas as pd
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time
import random
from datetime import datetime


def create_session():
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    return session


def fetch_product_links(main_url, session):
    product_links = []
    page_number = 1
    while True:
        url = f"{main_url}?page={page_number}"
        try:
            response = session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            links_on_page = 0
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/stock/' in href:
                    if href.startswith('http'):
                        full_url = href
                    else:
                        full_url = f"https://www.ouvrard.com{href}"
                    if full_url not in product_links:
                        product_links.append(full_url)
                        links_on_page += 1

            print(f"Page {page_number}: Found {links_on_page} product links.")
            
            if links_on_page == 0:
                break  # No more links found, stop pagination
            
            page_number += 1
            time.sleep(random.uniform(1, 3))  # Delay to avoid being blocked
        except requests.exceptions.RequestException as e:
            print(f"Error fetching product links on page {page_number}: {e}")
            break
    
    print(f"Total product links found: {len(product_links)}")
    return product_links

    
def fetch_product_details(product_url, session):
    try:
        response = session.get(product_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        details = {}
        details['url'] = product_url

        # Extracting main details using the specific structure provided
        def get_value(tag, label):
            tag = soup.find(tag, text=label)
            if tag:
                value_tag = tag.find_next('h5') or tag.find_next('li')
                if value_tag:
                    return value_tag.text.strip()
            return None

        prix_tag = soup.find('div', class_='dis-price')
        if prix_tag:
            price_span = prix_tag.find('span', class_='color-green colorBlack1')
            if price_span:
                details['Prix'] = price_span.text.strip()

        details['Marque'] = get_value('strong', 'Marque')
        details['Modèle'] = get_value('strong', 'Modèle')
        details['Année'] = get_value('strong', 'Année')
        details['Disponible chez'] = get_value('strong', 'disponible chez')
        details["Nombre d'heures moteur"] = get_value('strong', "Nombre d'heures moteur")
        details["Nombre d'heures batteur"] = get_value('strong', "Nombre d'heures batteur")
        details["Nombre de secoueurs"] = get_value('strong', "Nombre de secoueurs")
        details["Puissance"] = get_value('strong', "Puissance")
        details["Broyeur"] = get_value('strong', "Broyeur")
        details["Eparpilleur"] = get_value('strong', "Eparpilleur")
        details["Nombre de RM"] = get_value('strong', "Nombre de RM")
        details["Chariot de coupe"] = get_value('strong', "Chariot de coupe")
        details["Dimension des pneus AV"] = get_value('strong', "Dimension des pneus AV")
        details["Dimension des pneus AR"] = get_value('strong', "Dimension des pneus AR")
        details["Caisson de dévers"] = get_value('strong', "Caisson de dévers")
        details["Mise en Avant"] = get_value('strong', "Mise en Avant")

        location_tag = soup.find('div', id='map')
        if location_tag:
            address_tag = location_tag.find('p')
            if address_tag:
                details["Où trouver cette occasion"] = address_tag.text.strip()

        return details
    except requests.exceptions.RequestException as e:
        print(f"Error fetching product details from {product_url}: {e}")
        return None

'''
def get_detail(soup, key):
    key_tag = soup.find('strong', string=key)
    if key_tag:
        value_tag = key_tag.find_next_sibling('li')
        if value_tag:
            return value_tag.text.strip()
    return None
'''




def main():
    session = create_session()
    main_url = 'https://www.ouvrard.com/occasions-fr-fr.htm'
    product_links = fetch_product_links(main_url, session)

    all_product_details = []
    for i, product_link in enumerate(product_links, 1):
        print(f"Processing link {i} of {len(product_links)}: {product_link}")
        details = fetch_product_details(product_link, session)
        if details:
            all_product_details.append(details)
            print(f"Successfully extracted details for link {i}")
        else:
            print(f"Failed to extract details for link {i}")
        time.sleep(random.uniform(3, 7))  # Adding a delay between requests
    
    if all_product_details:
        today_date = datetime.now().strftime("%Y-%m-%d")
        filename = f'product_details{today_date}.csv'
        df = pd.DataFrame(all_product_details)
        df.to_csv(filename, index=False)
        print("Data has been saved to product_details.csv")
    else:
        print("No product details found.")

if __name__ == "__main__":
    main()