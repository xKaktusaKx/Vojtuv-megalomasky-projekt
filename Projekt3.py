"""
    Project: project_3
    Author: Vojtěch Kusý
    Email: vojtechku123@gmail.com
    Discord: angry_vojta

    """

import requests
from bs4 import BeautifulSoup
import csv
import argparse

url = 'https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103'

def remove_after_last_slash(url):
    last_slash_index = url.rfind('/')
    return url[:last_slash_index] if last_slash_index != -1 else url

def step1(url, output_file):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.find_all('tr') #najde všechny řádky tabulky
        
        data = [] #ukládá data

        for row in rows:
            cells = row.find_all("td") #najde pro každý řádek buňky
            if len(cells) >= 2: #pokud má řádek má 2 buňka, zpracuje se
                cell1 = cells.pop(0) #buňka
                cell2 = cells.pop(0)
                links = cell1.find_all("a") #vezme všechna data
                if links:
                    link1 = links.pop(0)
                    href = link1.get("href")
                    url2 = remove_after_last_slash(url) + "/" + href

                    row_data = [cell1.get_text(strip=True), cell2.get_text(strip=True)]
                    step2(url2, data, row_data)
        
    
        with open(output_file, 'w', newline='', encoding='cp1250') as file:
            writer = csv.writer(file, delimiter=";") #přepíše do CSV
            writer.writerows(data)
    else:
        print("Chyba při získavání dat")

def step2(url, excel_rows, row_data): #krokus pokus
    response = requests.get(url) #stáhne obsah stánky
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.find_all('tr') #najde všechny řádky tabulky
        hlavicky = []
        
        for row in rows:
            cells = row.find_all("td") #najde pro každý řádek buňky
            if len(cells) == 9:
                cell1 = cells.pop(3)
                cell2 = cells.pop(3)
                platne_hlasy = cells.pop(5)
                row_data.extend([cell1.get_text(strip=True), cell2.get_text(strip=True), platne_hlasy.get_text(strip=True)])
            elif len(cells) == 5:
                nazev_strany = cells.pop(1).get_text(strip=True) #sebere to info
                celkem_hlas = cells.pop(1).get_text(strip=True)
                row_data.append(celkem_hlas) 
                hlavicky.append(nazev_strany)
        
        if not excel_rows:
            hlavicky = ['code', 'location', 'registered', 'envelopes', 'valid'] + hlavicky
            excel_rows.append(hlavicky)
        
        excel_rows.append(row_data)
    else:
        print("Chyba při získavání dat")

def main(url, output_file):
    step1(url, output_file)

if __name__ == '__main__': #Hooodně důležité
    parser = argparse.ArgumentParser(description='Web scraping script')
    parser.add_argument('url', type=str, help='URL of the website to scrape')
    parser.add_argument('output_file', type=str, help='Name of the output file')
    args = parser.parse_args()
    
    if not args.url or not args.output_file: #argumenty
        print("Chyba: Musíte zadat oba argumenty: URL a název výstupního souboru.")
    else:
        main(args.url, args.output_file)
