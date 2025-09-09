from rich.pretty import pprint
import time
import os
import platform
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from seleniumbase import SB
from pyvirtualdisplay.display import Display
from dotenv import load_dotenv
from .utils import retry


def get_chrome_path_windows():
    import winreg
    try:
        reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
        chrome_path, _ = winreg.QueryValueEx(key, None)
        return chrome_path
    except FileNotFoundError:
        return None

class WebScraper:
    def __init__(self, user_data_dir=None, **seleniumbase_kwargs):
        """
        Prepara a configuração para o WebScraper.
        O driver SB será inicializado ao entrar no contexto 'with'.
        """
        print("🚀 Configurando WebScraper...")
        self.display = None
        self.sb = None
        self.sb_context = None 
        self.sb_kwargs = {}
  
        BASEDIR = os.path.abspath(os.path.dirname(__file__))
        load_dotenv(os.path.join(BASEDIR, '../.env'))
        
        env = os.getenv("ENV", "prod")
        self.current_platform = platform.system()
        
        print(f"🔍 ENV: '{env}'")
        print(f"💻 Sistema: {self.current_platform}")

        if user_data_dir:
            base_user_data_dir = os.path.join(BASEDIR, "user_data_dir")
            os.makedirs(base_user_data_dir, exist_ok=True)

            full_path = os.path.join(base_user_data_dir, user_data_dir)
            os.makedirs(full_path, exist_ok=True)
            
            print(f"👤 Usando perfil do Chrome em: {full_path}")
            self.sb_kwargs.update({
                'user_data_dir': full_path
            })
        
        if env == 'dev':
            print("🛠️ Modo DESENVOLVIMENTO")
            self.sb_kwargs.update({
                'incognito': False,
                'guest_mode': False,
                'headless': False,
                'window_size': '1366,768'
            })
        else:
            print("🖥️ Modo PRODUÇÃO")
            self.sb_kwargs.update({
                'uc': True,
                'undetectable': True,
                'uc_cdp_events': True,
                'incognito': False,
                'guest_mode': False,
                'window_size': '1920,1080',
            })

            if self.current_platform == "Windows":
                chrome_path = get_chrome_path_windows()
                if chrome_path:
                    self.sb_kwargs.update({
                        'binary_location': chrome_path
                    })
        
        self.sb_kwargs.update(seleniumbase_kwargs)

    def __enter__(self):
        """
        Inicializa o driver SB e o display virtual (se Linux)
        ao entrar no bloco 'with'.
        """
        if self.current_platform == 'Linux' and not self.sb_kwargs.get('headless'):
            print("🖥️ Iniciando display virtual para Linux...")
            self.display = Display(visible=0, size=(1920, 1080))
            self.display.start()

        print("🔧 Configurações SeleniumBase:")
        for key, value in self.sb_kwargs.items():
            print(f"   {key}: {value}")

        try:
            print("⏳ Inicializando driver SB...")
            self.sb_context = SB(**self.sb_kwargs)
            self.sb = self.sb_context.__enter__()                  
            print("✅ Driver SB inicializado com sucesso!")
            return self
        except Exception as e:
            print(f"❌ Erro ao inicializar driver SB: {e}")
            if self.display:
                self.display.stop()
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Fecha o driver SB e o display virtual (se aplicável)
        ao sair do bloco 'with'.
        """
        print("🔄 Fechando WebScraper...")
        
        if hasattr(self, 'sb_context') and self.sb_context:
            try:
                self.sb_context.__exit__(exc_type, exc_val, exc_tb)
                print("✅ SB fechado com sucesso!")
            except Exception as e:
                print(f"⚠️ Erro ao fechar SB: {e}")
        
        if self.display:
            try:
                self.display.stop()
                print("✅ Display virtual fechado!")
            except Exception as e:
                print(f"⚠️ Erro ao fechar display: {e}")
        
        print("✅ WebScraper fechado com sucesso!")

    def go_to(self, url, reconnect_time=5):
        print(f"🌐 Navegando para: {url}") 
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            print(f"🔗 URL corrigida para: {url}")
        self.sb.uc_open_with_reconnect(url, reconnect_time)
        current = self.sb.get_current_url()
        print(f"✅ Página carregada: {current}")
        return current
    
    def current_url(self):
        return self.sb.get_current_url()
    
    def sleep(self, secs):
        return time.sleep(secs)
    
    def open_new_tab(self, url):
        print("🆕 Abrindo nova aba...")
        self.sb.open_new_window()
        current = self.go_to(url)
        print(f"✅ Nova aba aberta em: {current}")
        return current

    def solve_captcha(self):
        print("🤖 Tentando resolver captcha...")
        try:
            self.sb.uc_gui_click_captcha()
            self.sb.uc_gui_handle_captcha()
            print("✅ Captcha resolvido com sucesso!")
            return True
        except Exception as e:
            print(f"❌ Erro ao resolver captcha: {e}")
            return False
             
    def visibility_of_element_located(self, timeout=5, delay=0, max_retries=2, wait_time=5):
        """Cria um localizador para um elemento visível."""
        return Locators(self.sb, timeout, EC.visibility_of_element_located, delay, max_retries, wait_time)
    
    def invisibility_of_element_located(self, timeout=5, delay=0, max_retries=2, wait_time=5):
        """Cria um localizador para um elemento invisível."""
        return Locators(self.sb, timeout, EC.invisibility_of_element_located, delay, max_retries, wait_time)
    
    def presence_of_element_located(self, timeout=5, delay=0, max_retries=2, wait_time=5):
        """Cria um localizador para um elemento que deve estar presente no DOM e visível na página."""
        return Locators(self.sb, timeout, EC.presence_of_element_located, delay, max_retries, wait_time)
    
    def element_to_be_clickable(self, timeout=5, delay=0, max_retries=2, wait_time=5):
        """Cria um localizador para um elemento que deve estar visível e habilitado para clique na página."""
        return Locators(self.sb, timeout, EC.element_to_be_clickable, delay, max_retries, wait_time)

    def frame_to_be_available_and_switch_to_it(self, timeout=10, delay=0, max_retries=2, wait_time=5):
        return Locators(self.sb, timeout, EC.frame_to_be_available_and_switch_to_it, delay, max_retries, wait_time)

class Locators:
    def __init__(self, sb, timeout, wait_method, delay, max_retries, wait_time) -> None:
        self.sb = sb
        self.timeout = timeout
        self.wait_method = wait_method
        self.delay = delay
        self.max_retries = max_retries
        self.wait_time = wait_time

    def _find_element(self, selector, by):
        if self.delay > 0:
            print(f"⏱️ Aguardando {self.delay}s antes de localizar elemento...")
            time.sleep(self.delay)
        
        print(f"🔍 Localizando elemento: {selector[:70]}...")
        
        try:
            wait = WebDriverWait(self.sb.driver, self.timeout)
            element = wait.until(self.wait_method((by, selector)))
            
            print("✅ Elemento encontrado!")
            return Actions(element, self.sb, self.max_retries, self.wait_time, selector, by)
            
        except TimeoutException:
            print(f"❌ Tempo limite excedido. Elemento não encontrado após {self.timeout}s.")
            raise
        except Exception as e:
            print(f"❌ Erro ao localizar elemento: {e}")
            raise

    def by_xpath(self, xpath):
        return self._find_element(xpath, By.XPATH)

    def by_tag_name(self, tag_name):
        return self._find_element(tag_name, By.TAG_NAME)
    
    def by_css_selector(self, css_selector):
        return self._find_element(css_selector, By.CSS_SELECTOR)

class Actions:
    def __init__(self, element, sb, max_retries, wait_time, selector=None, by=By.CSS_SELECTOR) -> None:
        self.element = element
        self.sb = sb
        self.max_retries = max_retries
        self.wait_time = wait_time
        self.selector = selector
        self.by = by
        self.action_chains = ActionChains(self.sb.driver)

    @retry()
    def scroll_to_view(self):
        """Rola a página para que o elemento fique visível."""
        print("🔄 Rolando para o elemento...")
        self.sb.execute_script("arguments[0].scrollIntoView({block: 'center'});", self.element)
        return self

    @retry()
    def remove(self):
        print("🗑️ Removendo elemento...")
        if self.element:
            return self.sb.execute_script("arguments[0].remove();", self.element)
        elif self.selector:
            return self.sb.execute_script(f"document.querySelector('{self.selector}').remove();")

    @retry()
    def send_keys(self, keys):
        display_keys = keys if len(keys) < 20 else keys[:20] + "..."
        print(f"⌨️ Digitando: {display_keys}")
        if self.selector:
            return self.sb.type(self.selector, keys, by=self.by)
        else:
            return self.sb.type(self.element, keys)
    
    @retry()
    def click(self):
        print("👆 Clicando no elemento...")
        try:
            if self.selector:
                return self.sb.click(self.selector, by=self.by)
            else:
                return self.element.click()
        except Exception as e:
            print(f"⚠️ Erro ao clicar com SeleniumBase: {e}")
            if self.element:
                print("🔄 Tentando rolar para o elemento e clicar via JS...")
                self.sb.execute_script("arguments[0].scrollIntoView({block: 'center'});", self.element)
                self.sb.execute_script("arguments[0].click();", self.element)
                return
            raise

    @retry()
    def double_click(self, x_offset=0, y_offset=0):
        print(f"👆👆 Duplo clique (offset: {x_offset}, {y_offset})...")
        self.action_chains.move_to_element(self.element)
        self.action_chains.move_by_offset(x_offset, y_offset)
        return self.action_chains.double_click().perform() 
    
    @retry()
    def clear(self):
        print("🧹 Limpando campo...")
        return self.element.send_keys(Keys.CONTROL + 'a' + Keys.DELETE)
    
    @retry()
    def get_text(self):
        if self.element:
            text = self.element.text.strip()
        elif self.selector:
            text = self.sb.get_text(self.selector, by=self.by).strip()
        else:
            text = ""
        
        print(f"📄 Texto obtido: {text[:70]}...")
        return text
    
    @retry()
    def get_attribute(self, attr):
        if self.element:
            value = self.element.get_attribute(attr)
        elif self.selector:
            value = self.sb.get_attribute(self.selector, attr, by=self.by)
        else:
            value = ""

        print("value: ", value)
        
        if value:
            value = value.strip()
            print(f"🏷️ Atributo '{attr}': {value[:70]}...")
        else:
            print(f"🏷️ Atributo '{attr}': (vazio)")
            
        return value or ""
    
    @retry()
    def get_value(self):
        print("💾 Obtendo valor do elemento...")
        value = ""

        try:
            if self.element:
                value = self.element.get_property("value") or ""
            elif self.selector:
                value = self.sb.get_value(self.selector, by=self.by) or ""
        except Exception as e:
            print(f"⚠️ Erro ao obter valor: {e}")
            value = ""

        value = value.strip()
        display_value = value if len(value) < 10 else value[:10] + "..."
        print(f"💾 Valor obtido: {display_value}")
        return value
    
    @property
    def find_elements(self):
        return ListActions(self.element, self.sb, self.max_retries, self.wait_time)
    
class ListActions:
    def __init__(self, element, sb, max_retries=2, wait_time=5):
        self.element = element
        self.sb = sb
        self.max_retries = max_retries
        self.wait_time = wait_time

    @retry()
    def by_css_selector(self, css_selector):
        print(f"🔍 Buscando elementos por CSS: {css_selector}")
        elements = self.element.find_elements(By.CSS_SELECTOR, css_selector)
        print(f"✅ Encontrados {len(elements)} elementos")
        return [
            Actions(el, self.sb, self.max_retries, self.wait_time)
            for el in elements
        ]

    @retry()
    def by_tag_name(self, tag_name):
        print(f"🔍 Buscando elementos por TAG: {tag_name}")
        elements = self.element.find_elements(By.TAG_NAME, tag_name)
        print(f"✅ Encontrados {len(elements)} elementos")
        return [
            Actions(el, self.sb, self.max_retries, self.wait_time)
            for el in elements
        ]


