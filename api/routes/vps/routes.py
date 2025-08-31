from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.web_scraper import WebScraper
import os
from dotenv import load_dotenv
import time
# Invoke-RestMethod -Uri "http://127.0.0.1:5000/get-code-for-access-token" -Method Get

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '../.env'))

router = APIRouter()

@router.post("/reset-baserow-db")
async def reset_baserow_db():
    scraper = WebScraper()
    try:
        email = os.getenv("EMAIL")
        password = os.getenv("PASSWORD")

        if not email or not password:
            print('EMAIL ou PASSWORD não estão definidos no .env')
            raise ValueError("EMAIL ou PASSWORD não estão definidos no .env")

        scraper.go_to('http://147.93.15.64:3000/projects/3fit/postgres/baserow-db')

        scraper \
            .visibility_of_element_located() \
            .by_xpath('/html/body/div[1]/div/div/div[1]/div/form/div/div[1]/div/input') \
            .send_keys(email)

        scraper \
            .visibility_of_element_located(delay=1) \
            .by_xpath('/html/body/div[1]/div/div/div[1]/div/form/div/div[2]/div/input') \
            .send_keys(password)

        scraper \
            .visibility_of_element_located(delay=1) \
            .by_xpath('/html/body/div[1]/div/div/div[1]/div/form/div/div[4]/button') \
            .click()

        scraper \
            .visibility_of_element_located(delay=1) \
            .by_xpath('/html/body/div[1]/div/div[2]/div/div[2]/div/div/div/div[1]/div/div[1]/button[1]') \
            .click()

        scraper \
            .visibility_of_element_located(delay=4) \
            .by_xpath('/html/body/div[1]/div/div[2]/div/div[2]/div/div/div/div[1]/div/div[1]/button[1]') \
            .click()
        
        time.sleep(15)

        return JSONResponse(content={'status': 'ok', 'message': 'Scraping executado com sucesso'})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        scraper.quit()