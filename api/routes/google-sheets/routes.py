from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from app.web_scraper import WebScraper
import os
from dotenv import load_dotenv
import time
import re
from services.gmail.gmail import get_emails, authenticate_gmail
# Invoke-RestMethod -Uri "http://127.0.0.1:5000/format-table?target_row=335" -Method Get

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '../.env'))

router = APIRouter()

def set_interval(interval: str, target_row: int = None) -> str:
    return re.sub(
        r"(\D+)(\d+)$",
        lambda m: m.group(1) + str(target_row if target_row is not None else int(m.group(2)) + 1),
        interval
    )


@router.get("/format-table")
async def test(target_row: int = Query(None)):
    with WebScraper(user_data_dir="chrome_profile") as scraper:
        try:
            gmail_email = os.getenv("GMAIL_EMAIL")
            gmail_password = os.getenv("GMAIL_PASSWORD")

            scraper.go_to('https://docs.google.com/spreadsheets/d/1Mzii6y3vpqPhuo8eChW0wBvFxW_HHEQR4DicMvDwbY4/edit?gid=1595357938#gid=1595357938')

            chrome_login_button = None

            try:
                chrome_login_button = scraper.element_to_be_clickable(delay=2, timeout=8).by_xpath('//a[@aria-label="Fazer login"]')
            except:
                pass

            if chrome_login_button:
                chrome_login_button.click()

                scraper.visibility_of_element_located().by_xpath('/html/body/div[2]/div[1]/div[2]/c-wiz/main/div[2]/div/div/div[1]/form/span/section/div/div/div[1]/div[1]/div[1]/div/div[1]/input').send_keys(gmail_email)
                scraper.element_to_be_clickable().by_xpath('/html/body/div[2]/div[1]/div[2]/c-wiz/main/div[3]/div/div[1]/div/div/button').click()

                scraper.visibility_of_element_located().by_xpath('/html/body/div[2]/div[1]/div[2]/c-wiz/main/div[2]/div/div/div/form/span/section[2]/div/div/div[1]/div[1]/div/div/div/div/div[1]/div/div[1]/input').send_keys(gmail_password)
                scraper.element_to_be_clickable().by_xpath('/html/body/div[2]/div[1]/div[2]/c-wiz/main/div[3]/div/div[1]/div/div/button').click()
            
            scraper.element_to_be_clickable().by_xpath('//div[@class="waffle-namedtable-gridpill-table-menu-button-wrapper"]').click() # /html/body/div[4]/div/div[2]/div/div[5]/div[1]/div/div[2]/div[2]/div[9]/div/div/div/div[3]/div/div[4]
            scraper.visibility_of_element_located(delay=2).by_xpath('//span[@class="goog-menuitem-label" and text()="Ajustar o intervalo da tabela"]').click()

            interval_input = scraper.visibility_of_element_located().by_xpath('//input[@aria-label="Intervalo"]')
            interval_value = interval_input.get_value()

            if target_row is not None:
                new_interval = set_interval(interval_value, target_row)
            else:
                new_interval = set_interval(interval_value)

            interval_input.clear()
            interval_input.send_keys(new_interval)
            
            scraper.element_to_be_clickable().by_xpath('//button[text()="OK"]').click()

            scraper.sleep(2)
            return JSONResponse(content={'status': 'ok', 'message': 'Scraping executado com sucesso'})
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
