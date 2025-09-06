import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.web_scraper import WebScraper
from dotenv import load_dotenv, find_dotenv
from urllib.parse import urlparse, parse_qs
import time


BASEDIR = os.path.abspath(os.path.dirname(__file__))
CREDS_PATH = os.path.join(BASEDIR, "credentials.json")
TOKEN_PATH = os.path.join(BASEDIR, "token.json")
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail(scraper: WebScraper):
    """
    Realiza a autenticação com a API do Gmail.
    - Tenta carregar as credenciais do token.json.
    - Se expiradas, tenta renová-las (refresh).
    - Se não existirem, inicia um fluxo de autorização local.
    Retorna o objeto 'service' para interagir com a API.
    """
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(
            TOKEN_PATH, 
            scopes=SCOPES,
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Erro ao renovar o token: {e}")
                creds = None 
        
        if not creds:
            if not os.path.exists(CREDS_PATH):
                raise FileNotFoundError(
                    f"Arquivo 'credentials.json' não encontrado em {CREDS_PATH}. "
                    "Faça o download na sua página de credenciais do Google Cloud Console."
                )
                
            flow = Flow.from_client_secrets_file(
                CREDS_PATH, 
                scopes=SCOPES,
                redirect_uri="http://localhost"
            )
            auth_url, _ = flow.authorization_url(
                access_type='offline', 
                prompt='consent', 
                include_granted_scopes='true'
            )

            scraper.open_new_tab(auth_url)

            gmail_email = os.getenv("GMAIL_EMAIL")
            gmail_password = os.getenv("GMAIL_PASSWORD")

            scraper \
                .visibility_of_element_located(delay=1) \
                .by_xpath('/html/body/div[2]/div[1]/div[2]/c-wiz/main/div[2]/div/div/div[1]/form/span/section/div/div/div[1]/div[1]/div[1]/div/div[1]/input') \
                .send_keys(gmail_email)

            scraper \
                .visibility_of_element_located(delay=1) \
                .by_xpath('/html/body/div[2]/div[1]/div[2]/c-wiz/main/div[3]/div/div[1]/div/div/button') \
                .click()
            
            scraper \
                .visibility_of_element_located(delay=3, timeout=10) \
                .by_xpath('/html/body/div[2]/div[1]/div[2]/c-wiz/main/div[2]/div/div/div[1]/form/span/section[2]/div/div/div[1]/div[1]/div/div/div/div/div[1]/div/div[1]/input') \
                .send_keys(gmail_password)
                               
            scraper \
                .visibility_of_element_located(delay=2) \
                .by_xpath('/html/body/div[2]/div[1]/div[2]/c-wiz/main/div[3]/div/div[1]/div/div/button') \
                .click()
            
            scraper \
                .visibility_of_element_located(delay=2) \
                .by_xpath('/html/body/div[1]/div[1]/div[2]/div/div/div[3]/div/div[2]/div/div/button') \
                .click()
            
            scraper \
                .visibility_of_element_located(delay=2) \
                .by_xpath('/html/body/div[1]/div[1]/div[2]/div/div/div[3]/div/div/div[2]/div/div/button') \
                .click()
            
            current_url = scraper.current_url(wait_change=True)
            parsed_url = urlparse(current_url)
            params = parse_qs(parsed_url.query)
            code = params.get("code", [None])[0]

            flow.fetch_token(code=code)
            creds = flow.credentials

        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
            print(f"Credenciais salvas em {TOKEN_PATH}")

    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        print(f'Ocorreu um erro ao construir o serviço: {error}')
        return None

def get_emails(service):
    """
    Busca e exibe os 10 e-mails mais recentes da caixa de entrada.
    """
    if not service:
        print("Serviço do Gmail não está disponível. Abortando.")
        return []
    
    emails = []

    try:
        results = service.users().messages().list(userId='me', maxResults=10).execute()
        messages = results.get('messages', [])

        if not messages:
            print("Nenhum email encontrado na sua caixa de entrada.")
            return []
        else:
            for msg in messages:
                msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
                headers = msg_data['payload']['headers']
                
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'Sem Assunto')
                sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Remetente Desconhecido')

                emails.append({
                    "id": msg['id'],
                    "from": sender,
                    "subject": subject,
                    "snippet": msg_data['snippet']
                })

            return emails

    except HttpError as error:
        print(f'Ocorreu um erro ao buscar os emails: {error}')


