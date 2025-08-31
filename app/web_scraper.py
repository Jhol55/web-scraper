from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from dotenv import load_dotenv
from seleniumbase import Driver
import pyautogui
from pyvirtualdisplay.display import Display
import Xlib.display
import time
import os
import platform
from .utils import retry


class WebScraper:
    def __init__(self, **seleniumbase_kwargs):
        """
        Inicializa o driver do SeleniumBase mantendo a lógica original.
        Otimizado para funcionar em Windows e Linux.
        
        Args:
            **seleniumbase_kwargs: Argumentos para o SeleniumBase Driver
        """
        print("🚀 Inicializando WebScraper...")
        self.display = None
        
        BASEDIR = os.path.abspath(os.path.dirname(__file__))
        load_dotenv(os.path.join(BASEDIR, '../.env'))
        
        env = os.getenv("ENV", "prod")
        current_platform = platform.system()
        
        print(f"🔍 ENV: '{env}'")
        print(f"💻 Sistema: {current_platform}")
    
        default_kwargs = {
            'incognito': True,
            'guest_mode': True,
            'no_sandbox': True,
            'disable_gpu': False,   
            'headless': False
        }
        
        if env == 'dev':
            print(f"🛠️ Modo DESENVOLVIMENTO")
            default_kwargs.update({            
                'window_size': '1366,768',  
            })
        else:
            print(f"🖥️ Modo PRODUÇÃO")
            default_kwargs.update({
                'uc': True,   
                'window_size': '1920,1080',             
            })

            if current_platform != 'Windows':             
                default_kwargs.update({
                    'disable_gpu': True,
                })

                self.display = Display(visible=0, size=(1920,1080))
                self.display.start()
                os.environ['DISPLAY'] = self.display.new_display_var
                pyautogui._pyautogui_x11._display = Xlib.display.Display(os.environ['DISPLAY'])
        
        default_kwargs.update(seleniumbase_kwargs)
        
        print(f"🔧 Configurações SeleniumBase:")
        for key, value in default_kwargs.items():
            print(f"   {key}: {value}")
        
        try:
            print("⏳ Inicializando driver SeleniumBase...")
            self.driver = Driver(**default_kwargs)
            print("✅ Driver inicializado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao inicializar driver: {e}")
            raise

    def go_to(self, url):
        """Navega para uma URL e espera que a página carregue."""
        print(f"🌐 Navegando para: {url}")
        self.driver.get(url)
        current = self.driver.current_url
        print(f"✅ Página carregada: {current}")
        return current

    def current_url(self):
        """Retorna a URL atual do navegador."""
        return self.driver.current_url
    
    def get_screenshot_as_file(self, path):
        """Tira um screenshot e salva em um arquivo."""
        print(f"📸 Salvando screenshot: {path}")
        return self.driver.get_screenshot_as_file(path)
    
    def solve_captcha(self, timeout=30):
        """
        Resolve captchas automaticamente usando SeleniumBase
        
        Args:
            timeout (int): Tempo limite para resolver o captcha
            
        Returns:
            bool: True se o captcha foi resolvido, False caso contrário
        """
        print(f"🤖 Tentando resolver captcha (timeout: {timeout}s)...")
        try:
            self.driver.uc_gui_click_captcha(timeout=timeout)
            print("✅ Captcha resolvido com sucesso!")
            return True
        except Exception as e:
            print(f"❌ Erro ao resolver captcha: {e}")
            return False
    
    def bypass_cloudflare(self):
        """
        Bypassa proteção Cloudflare
        
        Args:
            timeout (int): Tempo limite para bypass
        """
        print(f"☁️ Tentando bypass Cloudflare")
        try:
            self.driver.uc_gui_click_captcha()
            print("✅ Cloudflare bypassado com sucesso!")
            return True
        except Exception as e:
            print(f"❌ Erro ao fazer bypass do Cloudflare: {e}")
            return False
        
    def quit(self):
        """Fecha o navegador."""
        print("🔄 Fechando WebScraper...")
        try:
            if self.display:
                self.display.stop()
            self.driver.quit()
            print("✅ WebScraper fechado com sucesso!")
        except Exception as e:
            print(f"⚠️ Erro ao fechar WebScraper: {e}")

    def visibility_of_element_located(self, timeout=5, delay=0, retry=True, max_tries=2, wait_time=5, check_result=False):
        """Cria um localizador para um elemento visível."""
        return Locators(self.driver, timeout, EC.visibility_of_element_located, delay, retry, max_tries, wait_time, check_result)
    
    def invisibility_of_element_located(self, timeout=5, delay=0, retry=True, max_tries=2, wait_time=5, check_result=False):
        """Cria um localizador para um elemento invisível."""
        return Locators(self.driver, timeout, EC.invisibility_of_element_located, delay, retry, max_tries, wait_time, check_result)
    
    def frame_to_be_available_and_switch_to_it(self, timeout=5, delay=0, retry=True, max_tries=2, wait_time=5, check_result=False):
        """Cria um localizador para um frame."""
        return Locators(self.driver, timeout, EC.frame_to_be_available_and_switch_to_it, delay, retry, max_tries, wait_time, check_result)


class Locators:
    def __init__(self, driver, timeout, expected_condition, delay, retry, max_tries=2, wait_time=5, check_result=False) -> None:
        self.driver = driver
        self.timeout = timeout
        self.expected_condition = expected_condition
        self.delay = delay
        self.retry = retry
        self.max_tries = max_tries
        self.wait_time = wait_time
        self.check_result = check_result
        self.element = None     
        self.web_driver_wait = WebDriverWait(driver, timeout)

    @retry()
    def by_xpath(self, xpath):
        if self.delay > 0:
            print(f"⏱️ Aguardando {self.delay}s antes de localizar elemento...")
            time.sleep(self.delay)
        
        print(f"🔍 Localizando elemento por XPATH: {xpath[:50]}...")
        element = self.web_driver_wait.until(self.expected_condition((By.XPATH, xpath)))
        print("✅ Elemento encontrado!")
        return Actions(element, self.driver, self.retry)
    
    @retry()
    def by_tag_name(self, tag_name):
        if self.delay > 0:
            time.sleep(self.delay)
        
        print(f"🔍 Localizando elemento por TAG: {tag_name}")
        element = self.web_driver_wait.until(self.expected_condition((By.TAG_NAME, tag_name)))
        print("✅ Elemento encontrado!")
        return Actions(element, self.driver, self.retry)
    
    @retry()
    def by_css_selector(self, css_selector):
        if self.delay > 0:
            time.sleep(self.delay)
        
        print(f"🔍 Localizando elemento por CSS: {css_selector}")
        element = self.web_driver_wait.until(self.expected_condition((By.CSS_SELECTOR, css_selector)))
        print("✅ Elemento encontrado!")
        return Actions(element, self.driver, self.retry)


class Actions:
    def __init__(self, element, driver, retry=True, max_tries=2, wait_time=5, check_result=False) -> None:
        self.element = element
        self.driver = driver
        self.retry = retry
        self.max_tries = max_tries
        self.wait_time = wait_time
        self.check_result = check_result
        self.action_chains = ActionChains(self.driver)

    @retry()
    def remove(self):
        print("🗑️ Removendo elemento...")
        return self.driver.execute_script(f"""arguments[0].parentNode.removeChild(arguments[0]);""", self.element)

    @retry()
    def send_keys(self, keys):
        display_keys = keys[:4] + "..." 
        print(f"⌨️ Digitando: {display_keys}")
        return self.element.send_keys(keys)
    
    @retry()
    def click(self):
        print("👆 Clicando no elemento...")      
        return self.element.click()
    
    @retry()
    def double_click(self, x_offset=0, y_offset=0):
        print(f"👆👆 Duplo clique (offset: {x_offset}, {y_offset})...")
        self.action_chains.move_to_element(self.element)
        self.action_chains.move_by_offset(x_offset, y_offset)
        return self.action_chains.double_click().perform() 
        
    @retry()
    def move(self):
        print("🖱️ Movendo para elemento...")
        return self.action_chains.move_to_element(self.element).perform()
    
    @retry()
    def clear(self):
        print("🧹 Limpando campo...")
        return self.element.send_keys(Keys.CONTROL + 'a' + Keys.DELETE)
    
    @retry()
    def get_value_of_css_property(self, property):
        return self.element.value_of_css_property(property)
    
    @retry()
    def get_id(self):
        return self.element.get_attribute('id').rstrip().lstrip()
    
    @retry()
    def get_class(self):
        return self.element.get_attribute('class').rstrip().lstrip()
    
    @retry()
    def get_text(self):
        text = self.element.text.rstrip().lstrip()
        print(f"📄 Texto obtido: {text[:50]}...")
        return text
    
    @retry()
    def get_attribute(self, attr):
        value = self.element.get_attribute(attr).rstrip().lstrip()
        print(f"🏷️ Atributo {attr}: {value[:50]}...")
        return value
    
    @retry()
    def get_value(self):
        value = self.element.get_property('value').rstrip().lstrip()
        display_value = value[:len(value)] if len(value) < 10 else value[:10] + "..."
        print(f"💾 Valor obtido: {display_value}")
        return value
    
    @property
    def find_elements(self):
        return FindElements(self.element, self.driver, self.retry)


class FindElements:
    def __init__(self, element, driver, retry, max_tries=2, wait_time=5, check_result=False) -> None:
        self.element = element
        self.driver = driver
        self.retry = retry
        self.max_tries = max_tries
        self.wait_time = wait_time
        self.check_result = check_result

    @retry()
    def by_css_selector(self, css_selector):
        print(f"🔍 Buscando elementos filhos por CSS: {css_selector}")
        elements = self.element.find_elements(By.CSS_SELECTOR, css_selector)
        print(f"✅ Encontrados {len(elements)} elementos")
        return [Actions(element, self.driver, self.retry) for element in elements]
    
    @retry()
    def by_tag_name(self, tag_name):
        print(f"🔍 Buscando elementos filhos por TAG: {tag_name}")
        elements = self.element.find_elements(By.TAG_NAME, tag_name)
        print(f"✅ Encontrados {len(elements)} elementos")
        return [Actions(element, self.driver, self.retry) for element in elements]