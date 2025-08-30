from flask import Flask, jsonify
from web_scraper import WebScraper
import os
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
from seleniumbase import SB
import time
# Invoke-RestMethod -Uri "http://127.0.0.1:5000/get-code-for-access-token" -Method Get
BASEDIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(BASEDIR, '../.env'))

app = Flask(__name__)

@app.route('/reset-baserow-db', methods=['POST'])
def reset_baserow_db():
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

        return jsonify({'status': 'ok', 'message': 'Scraping executado com sucesso'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        scraper.quit()


@app.route('/get-code-for-access-token', methods=['GET'])
def get_code_for_access_token():
    scraper = WebScraper()
    try:
        email = os.getenv("BLING_EMAIL")
        password = os.getenv("BLING_PASSWORD")

        if not email or not password:
            print('BLING_EMAIL ou BLING_PASSWORD não estão definidos no .env')
            raise ValueError("BLING_EMAIL ou BLING_PASSWORD não estão definidos no .env")

        scraper.go_to('https://www.bling.com.br/login?r=https%3A%2F%2Fwww.bling.com.br%2Fcadastro.aplicativos.php%23%2Flist')

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
        
        return jsonify({'status': 'ok', 'message': 'Scraping executado com sucesso', 'data' : { 'code': code }})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        scraper.quit()



if __name__ == '__main__':
    env = os.getenv("ENV")
    if (env == 'dev'):
        app.run(debug=True, port=5000)
    else:
        from waitress import serve
        print("✅ Aplicação iniciada com sucesso!")
        serve(app, host="0.0.0.0", port=5000)
