import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import os

# Importer les fonctions de gestion de la base depuis database.py
from database import create_connection, DB_PATH, insert_offre, fetch_offre_by_url

#################################################
# Fonction auxiliaire : Standardiser la date
#################################################

def standardiser_date_publication(texte):
    """
    Convertit une chaîne relative (ex: "il y a 15 minutes", "il y a 2 heures",
    "il y a 3 jours", "il y a 1 mois") en une date/heure absolue au format "YYYY-MM-DD HH:MM:SS".
    Si le format n'est pas reconnu, retourne la date actuelle.
    """
    now = datetime.now()
    texte = texte.lower()
    
    match = re.search(r"il y a (\d+)\s+minute", texte)
    if match:
        return (now - timedelta(minutes=int(match.group(1)))).strftime("%Y-%m-%d %H:%M:%S")
    
    match = re.search(r"il y a (\d+)\s+heure", texte)
    if match:
        return (now - timedelta(hours=int(match.group(1)))).strftime("%Y-%m-%d %H:%M:%S")
    
    match = re.search(r"il y a (\d+)\s+jour", texte)
    if match:
        return (now - timedelta(days=int(match.group(1)))).strftime("%Y-%m-%d %H:%M:%S")
    
    match = re.search(r"il y a (\d+)\s+mois", texte)
    if match:
        return (now - timedelta(days=int(match.group(1)) * 30)).strftime("%Y-%m-%d %H:%M:%S")
    
    return now.strftime("%Y-%m-%d %H:%M:%S")  # Si aucun format reconnu
#################################################
# Extraction des offres depuis une page HelloWork
#################################################

def extract_offres_from_page(soup):
    """
    Extrait les offres d'une page HelloWork.
    """
    liste_offres = []
    
    listings = soup.find_all("li", attrs={"data-id-storage-target": "item"})
    
    for listing in listings:
        try:
            a_tag = listing.find("a", href=True)
            relative_url = a_tag["href"] if a_tag else None
            offre_url = "https://www.hellowork.com" + relative_url if relative_url and relative_url.startswith("/fr-fr") else relative_url
            
            h3_tag = a_tag.find("h3") if a_tag else None
            if h3_tag:
                titre_tag = h3_tag.find("p", class_=lambda x: x and "tw-typo-l" in x)
                entreprise_tag = h3_tag.find("p", class_=lambda x: x and "tw-typo-s" in x)
                titre = titre_tag.get_text(strip=True) if titre_tag else "Titre inconnu"
                entreprise = entreprise_tag.get_text(strip=True) if entreprise_tag else "Entreprise inconnue"
            else:
                titre = "Titre inconnu"
                entreprise = "Entreprise inconnue"

            # Localisation : récupération du texte et séparation en ville et département

            # Séparer ville et département proprement
            loc_tag = listing.find(attrs={"data-cy": "localisationCard"})
            lieu = loc_tag.get_text(strip=True) if loc_tag else "Inconnu"

            # Séparer ville et département proprement
            ville, departement = "Inconnu", "Inconnu"
            match = re.search(r"^(.*) - (\d{2,3})$", lieu)  # Exemple : "Paris - 75"
            if match:
                ville, departement = match.groups()
            elif lieu.isdigit():  # Cas où seule le département est présent
                departement = lieu
            else:
                ville = lieu  # Si pas de tiret, on suppose que c'est uniquement une ville

            print(f"Ville: {ville}, Département: {departement}")  # Debug
                
            # Extraction du type de contrat
            contrat_tag = listing.find(attrs={"data-cy": "contractCard"})
            type_contrat = contrat_tag.get_text(strip=True) if contrat_tag else "Type inconnu"
            

            # Récupération de la rémunération
            remuneration_tag = listing.find("div", class_="tw-readonly tw-tag-attractive-s tw-w-fit tw-border-0")
            remuneration = remuneration_tag.get_text(strip=True) if remuneration_tag else None


            # Récupération de la durée (valeur et unité)
            duration_tag = listing.find("div", attrs={"data-cy": "contractTag"})
            duree_valeur = None
            duree_unite = None
            duree = None
            
            if duration_tag:
                text = duration_tag.get_text(strip=True)
                match = re.search(r"(\d+)\s*(mois|semaine|semaines|jour|jours|heure|heures)", text, re.IGNORECASE)
                if match:
                    valeur = int(match.group(1))
                    unite = match.group(2).lower()
                    duree = (valeur, unite)  # Stocker en tuple (valeur, unité)
        
            # Extraction et conversion de la date de publication
            date_tag = listing.find("div", class_="tw-typo-s tw-text-grey")
            texte_date = date_tag.get_text(strip=True) if date_tag else "il y a 0 heure"
            date_publication = standardiser_date_publication(texte_date)


            # Ajout automatique de la date d’ajout (date actuelle)
            date_ajout = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Email non extrait ici
            email = None
            
            # Domaine par défaut
            domaine = "Inconnu"
            
            # Mots-clés générés
            mots_cles = f"{entreprise},{titre},{ville},{type_contrat}"
            
            # Construction du tuple final
            offre_tuple = (
                entreprise, titre, offre_url, email, ville, departement, domaine, 
                type_contrat, remuneration, date_publication, duree, mots_cles
            )
            
            liste_offres.append(offre_tuple)
        except Exception as e:
            print("Erreur lors de l'extraction d'une offre:", e)
    
    return liste_offres

#################################################
# Scraping avec Pagination
#################################################

def scrape_hellowork(url_base, max_pages):
    """
    Scrape les offres depuis HelloWork en gérant la pagination.
    
    Paramètres :
      - url_base : URL de base avec les filtres souhaités (ex: "https://www.hellowork.com/fr-fr/emploi/recherche.html?st=date&c=Stage&d=all")
      - max_pages : nombre maximum de pages à scraper (défini par l'administrateur).
    
    Retourne : Liste de toutes les offres récupérées.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    all_offres = []
    
    for page_num in range(1, max_pages + 1):
        url_pagination = f"{url_base}&p={page_num}"
        print(f"Scraping page {page_num}: {url_pagination}")
        resp = requests.get(url_pagination, headers=headers)
        
        if resp.status_code != 200:
            print(f"Arrêt : la page {page_num} renvoie le code {resp.status_code}.")
            break
        
        soup = BeautifulSoup(resp.text, "html.parser")
        offres_page = extract_offres_from_page(soup)
        
        if not offres_page:
            print(f"Arrêt : aucune offre trouvée à la page {page_num}.")
            break
        
        print(f"Page {page_num} : {len(offres_page)} offres récupérées.")
        all_offres.extend(offres_page)
        
        # Option : arrêter si aucune nouvelle offre n'est trouvée sur une page
        new_count = 0
        for off in offres_page:
            # Vérifier si l'offre existe déjà
            if not fetch_offre_by_url(create_connection(DB_PATH), off[2]):
                new_count += 1
        if new_count == 0:
            print(f"Aucune nouvelle offre trouvée à la page {page_num}. Arrêt du scraping.")
            break
    
    print(f"Total offres récupérées : {len(all_offres)}")
    return all_offres

#################################################
# Insertion dans la Base de Données
#################################################

def insert_offres_en_base(conn, offres):
    """
    Insère les offres dans la base de données en évitant les doublons (basé sur l'URL).
    Retourne le nombre d'offres nouvellement insérées.
    """
    count_new = 0
    for off in offres:
        existing = fetch_offre_by_url(conn, off[2])  # off[2] correspond à l'URL
        if not existing:
            print("Debug offre_tuple :", offre_tuple)
            insert_offre(conn, off)
            count_new += 1
    return count_new

#################################################
# Fonction Main
#################################################

def main():
    # Demander à l'administrateur l'URL de base avec filtres
    url_base = input("Entrez l'URL de recherche HelloWork avec vos filtres (ex: https://www.hellowork.com/fr-fr/emploi/recherche.html?st=date&c=Stage&d=all): ").strip()
    
    # Demander le nombre de pages à scraper
    try:
        max_pages = int(input("Entrez le nombre maximum de pages à scraper : "))
    except ValueError:
        print("Nombre de pages invalide, utilisation de 50 par défaut.")
        max_pages = 50
    
    # Connexion à la base de données
    conn = create_connection(DB_PATH)
    if not conn:
        print("Impossible de se connecter à la base de données.")
        return
    
    # Scraper les offres depuis HelloWork
    offres = scrape_hellowork(url_base, max_pages)
    
    # Insérer les offres récupérées dans la base de données
    nb_new = insert_offres_en_base(conn, offres)
    print(f"{nb_new} nouvelles offres insérées dans la base.")
    
    conn.close()

if __name__ == "__main__":
    main()
