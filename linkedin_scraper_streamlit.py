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
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# 📌 Chemins par défaut sur Streamlit Cloud
CHROME_BIN_PATH = "/usr/bin/google-chrome"
CHROMEDRIVER_PATH = "/usr/bin/chromedriver"

# ✅ Configuration navigateur headless
options = Options()
options.binary_location = CHROME_BIN_PATH
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(CHROMEDRIVER_PATH)

# 🌐 Interface Streamlit
st.title("🔍 Scraper LinkedIn (profils)")

EMAIL = st.text_input("Adresse email LinkedIn", type="default")
PASSWORD = st.text_input("Mot de passe LinkedIn", type="password")
run = st.button("Lancer le scraping")

if run and EMAIL and PASSWORD:
    st.info("Connexion à LinkedIn...")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://www.linkedin.com/login")
        driver.find_element(By.ID, "username").send_keys(EMAIL)
        driver.find_element(By.ID, "password").send_keys(PASSWORD + Keys.RETURN)
        time.sleep(5)
        st.success("Connexion réussie !")

        url = "https://www.linkedin.com/search/results/people/?keywords=product"
        driver.get(url)
        time.sleep(5)
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
                st.warning(f"Erreur lors de l'extraction d’un profil : {e}")

        if results:
            with open("profils_linkedin.csv", "w", newline='', encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)

            st.success("✅ Profils extraits avec succès !")
            st.dataframe(results)
        else:
            st.warning("⚠️ Aucun profil détecté.")
    except Exception as e:
        st.error(f"❌ Erreur : {e}")
    finally:
        driver.quit()
