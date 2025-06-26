import requests
from bs4 import BeautifulSoup
from langdetect import detect
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_job_description(url):
    """
    Parse une offre d'emploi depuis une URL, en gérant JavaScript
    """
    # D'abord, essayer avec requests (plus rapide)
    try:
        print("   🔄 Tentative avec requests...")
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = ' '.join([p.get_text() for p in soup.find_all('p')])
        
        # Vérifier si on a du contenu utile
        if len(text.strip()) > 100 and "Enable JavaScript" not in text:
            print("   ✅ Contenu récupéré avec requests")
            langue = detect(text)
            return text.strip(), langue
        else:
            raise Exception("Contenu insuffisant ou JavaScript requis")
            
    except Exception as e:
        print(f"   ⚠️  Requests échoué: {str(e)}")
        print("   🔄 Tentative avec Selenium (JavaScript)...")
        
        # Configuration de Selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Mode sans interface
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            # Initialisation du driver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Chargement de la page
            driver.get(url)
            
            # Attendre que la page se charge
            time.sleep(3)
            
            # Essayer de trouver le contenu principal
            try:
                # Attendre que du contenu se charge
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Récupérer tout le texte de la page
                page_text = driver.find_element(By.TAG_NAME, "body").text
                
                # Nettoyer le texte
                lines = [line.strip() for line in page_text.split('\n') if line.strip()]
                text = ' '.join(lines)
                
                print("   ✅ Contenu récupéré avec Selenium")
                
            except Exception as wait_error:
                print(f"   ⚠️  Erreur d'attente: {wait_error}")
                # Récupérer ce qu'on peut
                text = driver.page_source
                soup = BeautifulSoup(text, 'html.parser')
                text = soup.get_text()
                
            finally:
                driver.quit()
            
            # Vérifier qu'on a du contenu
            if len(text.strip()) < 50:
                raise Exception("Contenu insuffisant récupéré")
                
            langue = detect(text)
            return text.strip(), langue
            
        except Exception as selenium_error:
            print(f"   ❌ Selenium échoué: {selenium_error}")
            # Fallback : demander à l'utilisateur de copier-coller
            print("\n" + "="*60)
            print("🚨 IMPOSSIBLE DE PARSER AUTOMATIQUEMENT L'OFFRE")
            print("="*60)
            print("Le site nécessite une interaction manuelle.")
            print("Veuillez copier-coller le texte de l'offre ci-dessous:")
            print("(Appuyez sur Entrée deux fois pour terminer)")
            print("-" * 60)
            
            lines = []
            while True:
                line = input()
                if line == "" and len(lines) > 0 and lines[-1] == "":
                    break
                lines.append(line)
            
            text = ' '.join(lines).strip()
            if len(text) > 20:
                langue = detect(text)
                return text, langue
            else:
                return "Offre d'emploi - contenu non disponible", "fr"