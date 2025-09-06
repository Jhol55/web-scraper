from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.web_scraper import WebScraper
import os
from dotenv import load_dotenv
import time
import re
from services.gmail.gmail import get_emails, authenticate_gmail
# Invoke-RestMethod -Uri "http://127.0.0.1:5000/test" -Method Get

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '../.env'))

router = APIRouter()


@router.get("/test")
async def test():
    with WebScraper(uc=True) as scraper:
        try:
            tray_user = os.getenv("TRAY_USER")
            tray_password = os.getenv("TRAY_PASSWORD")

            gmail_email = os.getenv("GMAIL_EMAIL")
            gmail_password = os.getenv("GMAIL_PASSWORD")

            if not tray_user or not tray_password:
                print('TRAY_USER ou TRAY_PASSWORD não estão definidos no .env')
                raise ValueError("TRAY_USER ou TRAY_PASSWORD não estão definidos no .env")
            
            if not gmail_email or not gmail_password:
                print('GMAIL_EMAIL ou GMAIL_PASSWORD não estão definidos no .env')
                raise ValueError("GMAIL_EMAIL ou GMAIL_PASSWORD não estão definidos no .env")
            await scraper.teste()
            scraper.go_to('https://loja-s.tray.com.br/adm/login.php?loja=789987')

            scraper \
                .visibility_of_element_located(delay=1) \
                .by_xpath('/html/body/div[1]/div/div/div[1]/form/fieldset/div[1]/input') \
                .send_keys(tray_user)
            
            scraper \
                .visibility_of_element_located(delay=1) \
                .by_xpath('/html/body/div[1]/div/div/div[1]/form/fieldset/div[2]/div/input') \
                .send_keys(tray_password)
            
            scraper \
                .visibility_of_element_located(delay=1) \
                .by_xpath('/html/body/div[1]/div/div/div[1]/form/fieldset/button') \
                .click()
            
            try:
                scraper.solve_captcha()
                if scraper.frame_to_be_available_and_switch_to_it(timeout=15).by_xpath('/html/body/div[1]/div/div/div[1]/form/fieldset/div[3]/div/div/iframe'):
                    scraper \
                        .element_to_be_clickable(delay=1, timeout=60) \
                        .by_xpath('/html/body/div[2]/div[3]') \
                        .click()

                    time.sleep(10)
                            
                    scraper.solve_captcha()

                    scraper \
                        .visibility_of_element_located(delay=1) \
                        .by_xpath('/html/body/div[1]/div/div/div[1]/form/fieldset/div[1]/input') \
                        .send_keys(tray_user)
                
                    scraper \
                        .visibility_of_element_located(delay=1) \
                        .by_xpath('/html/body/div[1]/div/div/div[1]/form/fieldset/div[2]/div/input') \
                        .send_keys(tray_password)
                    
                    scraper \
                        .visibility_of_element_located(delay=1) \
                        .by_xpath('/html/body/div[1]/div/div/div[1]/form/fieldset/button') \
                        .click()
            except:
                pass
            
            
            try:
                wrong_code = None
                while wrong_code or wrong_code is None:
                    email = []
                    
                    try:
                        gmail_service = authenticate_gmail(scraper)
                        emails = get_emails(gmail_service)
                    except Exception as e:
                        print("❌ Erro ao buscar emails:", e)

                    tray_code = None
                    for email in emails:
                        if '3fit' in email.get('from', '').lower():
                            subject = email.get('subject')
                            match = re.match(r"(\d+)", subject)
                            if match:
                                tray_code = match.group(1)
                                break

                    scraper.switch_to_window(0)

                    scraper \
                        .visibility_of_element_located(delay=1) \
                        .by_xpath('/html/body/div[1]/div/div/div[1]/form/fieldset/div[2]/div/input') \
                        .send_keys(tray_code)
                    
                    scraper \
                        .visibility_of_element_located(delay=1) \
                        .by_xpath('/html/body/div[1]/div/div/div[1]/form/fieldset/div[2]/p[4]/span/input') \
                        .click()
                    
                    scraper \
                        .visibility_of_element_located(delay=1) \
                        .by_xpath('/html/body/div[1]/div/div/div[1]/form/fieldset/div[2]/p[4]/span/button') \
                        .click()
                    
                    if scraper.visibility_of_element_located(delay=1, timeout=5, max_tries=0).by_xpath('/html/body/div[1]/div/div/div[1]/form/fieldset/div[2]/p[4]/span/button'):
                        wrong_code = True
                        time.sleep(35)
                        scraper \
                            .visibility_of_element_located(delay=1, timeout=5) \
                            .by_xpath('/html/body/div[1]/div/div/div[1]/form/fieldset/div[2]/p[3]/a') \
                            .click()
                    else:
                        wrong_code=False
            except:
                pass
            

            try:
                scraper \
                    .visibility_of_element_located(delay=1, timeout=2) \
                    .by_xpath('/html/body/div[1]/div/div[1]/div[1]/div[3]/div/div[1]/div/div[2]/div[2]/div[2]/div/div[2]/button') \
                    .click()  
            except:
                pass

            scraper.go_to(
                'https://www.loja.3fit.com.br/admin/marketing/carts?sort=id&page%5Bsize%5D=200&page%5Bnumber%5D=1&filter%5Borigin%5D=Todos%3A&filter%5Bwith_customer%5D=Todos%3A'
            )

            tbody = scraper \
                .visibility_of_element_located(delay=10, timeout=30) \
                .by_xpath('/html/body/div[1]/div/div[3]/div[1]/div/div[2]/div/div[1]/div[2]/div/div[2]/table/tbody')
            
            trs = tbody.find_elements.by_css_selector('.abandoned-cart-list__row')
            for tr in trs:
                tds = tr.find_elements.by_css_selector('td')
                try:
                    tds[6].find_elements.by_css_selector('.mdi-whatsapp')[0].click()
                    print("passei1")
                    a = scraper.visibility_of_element_located(delay=5, timeout=30).by_xpath('/html/body/div[7]/div[1]/div/div/div/div[3]/div[2]/table/tbody/tr[1]/td[1]/div/input')
                    a.click()
                    print("element: ", a)
                    print("passei2")
                    scraper.element_to_be_clickable(timeout=10).by_xpath('/html/body/div[7]/div[1]/div/div/header/button').click()

                except:
                    pass
            
            time.sleep(5)

            return JSONResponse(content={'status': 'ok', 'message': 'Scraping executado com sucesso'})
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))