import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# URL dari halaman web yang akan di-scrape
urls = ['https://wikiliq.org/brands/vodka/']

# Inisialisasi driver Selenium (gunakan path ke chromedriver Anda)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Menjalankan browser dalam mode headless
driver = webdriver.Chrome(options=chrome_options)

def scrape(url):
    print(f"Scraping URL: {url}")
    driver.get(url)
    all_data = []
    
    # Tunggu sampai elemen 'prod-row' muncul
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'prod-row')))
    print("Element 'prod-row' found")

    while True:
        # Ambil konten halaman dengan BeautifulSoup
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        # Semua tabel
        tabel = soup.find('div', class_='prod-row')
        if tabel:
            print("Processing table rows")
            # Mencari semua elemen a dengan class 'brandcard' di dalam tabel
            tabel_select_s = tabel.find_all('a', class_='brandcard')
            for tabel_select in tabel_select_s:
                # Mencari elemen img di dalam tabel_select
                logo = tabel_select.find('img')
                src = logo.get('src') if logo else None

                # Nama perusahaan
                name_company = tabel_select.find('div', class_='brandtitle').text.strip()

                # Produk yang dimiliki
                product_have = tabel_select.find('div', class_='brandcount').text.strip()
                clean_product_have = product_have.replace('Products:', '').strip()

                # Negara (bendera)
                flag = tabel_select.find('div', class_='brandcountry')
                flag_img_src = None
                if flag:
                    flag_img = flag.find('img')
                    flag_img_src = flag_img.get('src') if flag_img else None

                # Ekstrak nama negara dari URL gambar
                if flag_img_src:
                    flag_img_src = flag_img_src.split('/')[-1].replace('.png', '').replace('-', ' ')

                # Menyimpan data ke dalam list
                all_data.append({
                    'Logo': src,
                    'Company Name': name_company,
                    'Product Have': clean_product_have,
                    'Country': flag_img_src
                })
                print(f"Added: {name_company} with Country: {flag_img_src}")
        
        # Coba klik tombol "more" jika ada
        try:
            more_button = driver.find_element(By.CLASS_NAME, 'load-more-brands')  # Ganti dengan selector yang sesuai
            more_button.click()
            print("Clicked 'Load More' button")
            time.sleep(2)  # Tunggu beberapa detik agar konten baru dimuat
        except Exception as e:
            print(f"No 'Load More' button found or other error: {e}")
            break
    
    return all_data

# List untuk menyimpan semua data
all_data = []

# Loop melalui semua URL dan mengumpulkan data
for url in urls:
    all_data.extend(scrape(url))

# Membuat DataFrame dari semua data
df = pd.DataFrame(all_data)
print("DataFrame created")

# Menyimpan DataFrame ke file CSV
csv ='vodka.csv'
df.to_csv(csv, index=False)
print(f"Data has been saved to {csv}")

# Menutup driver
driver.quit()
print("Driver closed")
