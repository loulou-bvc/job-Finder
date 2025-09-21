from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# 📌 Configuration du WebDriver
CHROMEDRIVER_PATH = "/opt/homebrew/bin/chromedriver"  
service = Service(CHROMEDRIVER_PATH)
options = webdriver.ChromeOptions()

# ✅ Mode navigation privée
options.add_argument("--incognito")

# ✅ Modifier l’User-Agent pour être moins détectable
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36")

# ✅ Empêcher Selenium d’être détecté
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

# ✅ Supprimer cookies et sessions pour éviter le tracking
options.add_argument("--disable-gpu") 
options.add_argument("--start-maximized")
options.add_argument("--disable-extensions")
options.add_argument("--disable-popup-blocking")

driver = webdriver.Chrome(service=service, options=options)

# ⛔ Supprimer les traces Selenium
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# ✅ Charger la page d'accueil d'Indeed pour éviter `data:`
driver.get("https://fr.indeed.com/")

# ✅ Attendre que la page soit bien chargée
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

# 🚀 Nettoyer cookies et stockage pour éviter d'être détecté comme robot
try:
    driver.delete_all_cookies()
    driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
except:
    print("⚠️ Impossible d'effacer localStorage/sessionStorage (possible restriction).")

# 🏁 Saisie des paramètres
base_url = input("🔗 URL Indeed de la recherche : ").strip()
if "&start=" not in base_url:
    base_url += "&start="  # Ajoute le paramètre de pagination si absent

# 📌 Préremplissage des colonnes
print("\n💡 Laissez vide pour ne pas préremplir une colonne.")
default_type_contrat = input("📌 Type de contrat : ").strip()
default_ville = input("🌍 Ville : ").strip()
default_departement = input("📍 Département : ").strip()
default_domaine = input("💼 Domaine : ").strip()

# 📄 Nombre de pages à scraper
while True:
    try:
        nombre_pages = int(input("📑 Combien de pages souhaitez-vous scraper ? (10 offres par page) : "))
        break
    except ValueError:
        print("❌ Veuillez entrer un nombre valide.")

# 📝 Fonction pour extraire les offres

# 📝 Fonction pour extraire les offres
def extract_jobs(page):
    # Vérifier si "&start=" est déjà présent dans l'URL
    if "&start=" in base_url:
        base_cleaned = base_url.split("&start=")[0]  # Supprime la pagination existante
    else:
        base_cleaned = base_url

    url = f"{base_cleaned}&start={page * 10}"  # 🔹 Générer correctement l'URL
    print(f"📡 Scraping page {page + 1}/{nombre_pages}...")
    print(f"🔗 URL : {url}")

    driver.get(url)

    # ⏸️ Pause pour CAPTCHA
    input("⚠️ Si un CAPTCHA apparaît, résous-le puis appuie sur [ENTRÉE] pour continuer...")

    print("✅ CAPTCHA validé. Début du scraping...")
    time.sleep(3)  # Pause pour laisser la page charger
    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "job_seen_beacon"))
        )
    except:
        print("⚠️ Aucune offre trouvée sur cette page.")
        return []

    # 📌 Récupération des offres
    job_cards = driver.find_elements(By.CLASS_NAME, "job_seen_beacon")
    
    if not job_cards:
        job_cards = driver.find_elements(By.CLASS_NAME, "css-1ac2h1w")  # ⬅️ Test avec une autre classe
        print("🔍 Essai avec un autre sélecteur.")

    jobs = []
    
    for card in job_cards:
        try:
            title_element = card.find_element(By.CLASS_NAME, "jobTitle")
            url_element = card.find_element(By.TAG_NAME, "a")

            try:
                company_element = card.find_element(By.CLASS_NAME, "css-1h7lukg")
                company = company_element.text.strip()
            except:
                company = "Non précisé"

            try:
                location_element = card.find_element(By.CLASS_NAME, "css-1restlb")
                location = location_element.text.strip()
            except:
                location = default_ville if default_ville else "Non précisé"

            try:
                type_contrat_element = card.find_element(By.CLASS_NAME, "css-18z4q2i")
                type_contrat = type_contrat_element.text.strip()
            except:
                type_contrat = default_type_contrat if default_type_contrat else "Non précisé"

            title = title_element.text.strip() if title_element else "Non précisé"
            job_url = "https://fr.indeed.com" + url_element.get_attribute("href") if url_element else "Non disponible"

            departement = default_departement if default_departement else (
                location.split(" ")[-1] if location.split(" ")[-1].isdigit() else "Non précisé"
            )

            domaine = default_domaine if default_domaine else "Non précisé"

            job_data = [company, title, job_url, location, departement, domaine, type_contrat]
            jobs.append(job_data)

        except Exception as e:
            print(f"⚠️ Erreur sur une offre : {e}")

    return jobs

# 📌 Lancer le scraping sur plusieurs pages
all_jobs = []
for page in range(nombre_pages):
    all_jobs.extend(extract_jobs(page))

# 📂 Sauvegarde des résultats
df = pd.DataFrame(all_jobs, columns=['Entreprise', 'Titre', 'Lien', 'Ville', 'Département', 'Domaine', 'Type de Contrat'])
df.to_csv("indeed_offres.csv", index=False, encoding="utf-8")

print(f"\n✅ {len(all_jobs)} offres ont été enregistrées.")
driver.quit()
