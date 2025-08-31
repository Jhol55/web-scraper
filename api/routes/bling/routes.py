from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.web_scraper import WebScraper
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs


BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '../.env'))

router = APIRouter()

router.get("/get-code-for-access-token")
def get_code_for_access_token():
    scraper = WebScraper()
    try:
        email = os.getenv("BLING_EMAIL")
        password = os.getenv("BLING_PASSWORD")

        if not email or not password:
            print('BLING_EMAIL ou BLING_PASSWORD não estão definidos no .env')
            raise ValueError("BLING_EMAIL ou BLING_PASSWORD não estão definidos no .env")

        scraper.go_to('https://www.bling.com.br/login?r=https%3A%2F%2Fwww.bling.com.br%2Fcadastro.aplicativos.php%23%2Flist')

        scraper.bypass_cloudflare()

        scraper \
            .visibility_of_element_located(delay=1) \
            .by_xpath('/html/body/div[2]/form/div/div[1]/div/div[1]/input') \
            .send_keys(email) 
        
        scraper \
            .visibility_of_element_located(delay=1) \
            .by_xpath('/html/body/div[2]/form/div/div[1]/div/div[2]/div/input') \
            .send_keys(password)
        
        scraper \
            .visibility_of_element_located(delay=1) \
            .by_xpath('/html/body/div[2]/form/div/div[1]/div/button[1]') \
            .click()
        
        scraper \
            .visibility_of_element_located(delay=1) \
            .by_xpath('/html/body/div[7]/div[1]/div/div[3]/div[2]/div[2]/table/tbody/tr[2]') \
            .click()
        
        scraper \
            .visibility_of_element_located(delay=2) \
            .by_xpath('/html/body/div[7]/div[1]/div/div[3]/div[1]/ul/li[2]') \
            .click()
        
        invitation_link = scraper \
            .visibility_of_element_located(delay=2) \
            .by_xpath('/html/body/div[7]/div[1]/div/div[3]/div[2]/div[1]/div/div[4]/div/div/input') \
            .get_value()
            
        scraper.go_to(invitation_link)
        
        current_url = scraper.current_url()
        
        parsed_current_url = urlparse(current_url)
        query_params = parse_qs(parsed_current_url.query)
        
        code = query_params.get("code", [None])[0]
        
        return JSONResponse(content={'status': 'ok', 'message': 'Scraping executado com sucesso', 'data': {'code': code}})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        scraper.quit()