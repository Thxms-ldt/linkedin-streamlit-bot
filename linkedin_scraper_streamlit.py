# linkedin_scraper_streamlit.py
import os
import csv
import time
import streamlit as st
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

CHROME_BIN_PATH = "/usr/bin/chromium-browser"
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

options.binary_location = CHROME_BIN_PATH
service = Service(executable_path=CHROMEDRIVER_PATH)

driver = webdriver.Chrome(service=service, options=options)
# Charger les identifiants LinkedIn
load_dotenv()
EMAIL = os.getenv("LINKEDIN_EMAIL") or "TON_EMAIL_LINKEDIN"
PASSWORD = os.getenv("LINKEDIN_PASSWORD") or "TON_MDP_LINKEDIN"

st.title("🔍 LinkedIn Profile Scraper")

run = st.button("Lancer le scraping")

if run:
    st.info("🚀 Démarrage du navigateur...")

    # Configuration du navigateur compatible Streamlit Cloud
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get("https://www.linkedin.com/login")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        ).send_keys(EMAIL)
        driver.find_element(By.ID, "password").send_keys(PASSWORD + Keys.RETURN)
        time.sleep(5)
        st.success("✅ Connexion réussie !")

        url = "https://www.linkedin.com/search/results/people/?keywords=product"
        driver.get(url)
        time.sleep(3)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        profiles = soup.select("div.FvPOwKRhaVsTBWLnXXMnOPQunEM")

        results = []
        for prof in profiles:
            try:
                name_tag = prof.find('span', attrs={"aria-hidden": "true"})
                name = name_tag.text.strip() if name_tag else "N/A"

                job_tag = prof.find('div', class_='pWIDTtuKGUWausIySAtxTfPvqtvw')
                job = job_tag.text.strip() if job_tag else "N/A"

                location_tag = prof.find('div', class_='zHdpFoSrkxcBYktVsSPmXCViwtxTTFQcwY')
                location = location_tag.text.strip() if location_tag else "N/A"

                company_tag = prof.find('p', class_='entity-result__summary--2-lines')
                if not company_tag:
                    company_tag = prof.find('p')
                company = company_tag.text.strip() if company_tag else "N/A"

                link_tag = prof.find('a', href=True)
                profile_url = link_tag['href'] if link_tag else "N/A"

                results.append({
                    "Nom": name,
                    "Job": job,
                    "Localisation": location,
                    "Entreprise": company,
                    "Lien Profil": profile_url
                })
            except Exception as e:
                st.warning(f"Erreur profil : {e}")

        if results:
            with open("profils_linkedin.csv", "w", newline='', encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
            st.success("✅ Profils extraits et enregistrés dans profils_linkedin.csv !")
            st.dataframe(results)
        else:
            st.warning("⚠️ Aucun profil détecté.")
    except Exception as e:
        st.error(f"❌ Erreur inattendue : {e}")
    finally:
        driver.quit()

