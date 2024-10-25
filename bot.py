from dotenv import load_dotenv
import os
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, WebDriverException, NoAlertPresentException, StaleElementReferenceException
import random
import time
from datetime import timedelta
import logging
import subprocess
from fake_useragent import UserAgent

from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager

class BlogBot:
    def __init__(self, url, use_vpn=False, vpn_location=None, max_retries=3, window_size=(1280, 720), geckodriver_path=None):
        load_dotenv()
        self.setup_logging()

        # Load environment variables
        self.main_url = os.getenv('MAIN_URL')
        self.url = url if url else self.main_url  # Use provided URL or fall back to MAIN_URL

        self.max_ads_to_click = 30  # Define the target number of ads to click
        self.ad_click_timeout = 30 * 60  # Set a timeout for ad clicks in seconds (e.g., 30 minutes)
        self.start_time = None

        # Debug logging
        self.logger.info(f"Initializing BlogBot with URL: {self.url}")
        
        if not self.url:
            raise ValueError("No valid URL provided. Please check your .env file or provide a URL.")
        
        self.ua = UserAgent()

        # self.user_agents = self.generate_user_agent_list()
        self.window_size = window_size
        self.driver = None
        self.total_ads_clicked = 0
        self.clicked_ads = set()  # This set will store unique ad identifiers
        
        # ******************** Firefox Setup ********************
        # self.options = FirefoxOptions()
        # self.options.add_argument('-private')  # This enables incognito mode in Firefox
        # self.options.add_argument(f'--width={self.window_size[0]}')
        # self.options.add_argument(f'--height={self.window_size[1]}')
        # self.options.set_preference("dom.webdriver.enabled", False)
        # self.options.set_preference('useAutomationExtension', False)
        # self.options.set_preference("general.useragent.override", self.ua.random)
        # self.geckodriver_path = geckodriver_path or r'C:\Program Files\geckodriver-v0.35.0-win64\geckodriver.exe'  # Updated default path

        # ******************** Chrome Setup ********************
        self.options = Options()
        self.options.add_argument(f'--window-size={self.window_size[0]},{self.window_size[1]}')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        # user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'
        # self.options.add_argument(f'user-agent={user_agent}')
        self.options.add_argument(f'user-agent={self.ua.random}')
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-popup-blocking")
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-infobars')
        # Disable SSL verification
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        # This can help bypass some anti-bot measures
        self.options.add_argument(f'user-data-dir={os.path.expanduser("~")}/chrome-data')

        # To enable incognito mode
        self.options.add_argument("--incognito")


        if use_vpn:
            self.connect_vpn(vpn_location)
        
        self.driver = self.initialize_driver(max_retries)
        # self.driver.set_page_load_timeout(60)  # 60 seconds timeout
        self.wait = WebDriverWait(self.driver, 30)  # Increased default wait time

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def generate_user_agent_list(self):
        # Generate a list of diverse user agents
        browsers = ['chrome', 'firefox', 'safari', 'opera']
        platforms = ['windows', 'macos', 'linux']
        user_agents = []
        for _ in range(50):  # Generate 50 unique user agents
            browser = random.choice(browsers)
            platform = random.choice(platforms)
            try:
                user_agents.append(self.ua[f'{browser} {platform}'])
            except KeyError as e:
                self.logger.warning(f"Error occurred during getting browser: {browser}{platform}, but was suppressed with fallback. Error: {e}")
                # If the specific combination is not available, use a random user agent
                user_agents.append(self.ua.random)
        return list(set(user_agents))  # Remove duplicates

    def get_random_user_agent(self):
        return random.choice(self.user_agents)


    def initialize_driver(self, max_retries):
        for attempt in range(max_retries):
            try:
                # ******************** FireFox Setup ********************
                # if not os.path.exists(self.geckodriver_path):
                #     raise FileNotFoundError(f"Geckodriver not found at {self.geckodriver_path}")
                
                # service = Service(self.geckodriver_path)
                # driver = webdriver.Firefox(service=service, options=self.options)

                # ******************** Chrome Setup ********************
                service = Service(r"C:\Program Files\chromedriver-win64\chromedriver.exe")
                # user_agent = self.get_random_user_agent()
                # self.options.add_argument(f'user-agent={user_agent}')
                self.logger.info(f"Using User Agent: {self.ua.random}")
                driver = webdriver.Chrome(service=service, options=self.options)


                # # Randomize screen and viewport size
                # width = random.randint(1024, 1920)
                # height = random.randint(768, 1080)
                # driver.set_window_size(width, height)
                # print(f"Set window size to {width}x{height}")
                # driver.set_window_size(*self.window_size)
                # print(f"Set window size to {self.window_size[0]}x{self.window_size[1]}")
                
                # Disable WebDriver flags
                self.disable_webdriver_flags(driver)
                
                # # After initializing the driver, get and print the initial fingerprint
                # initial_fingerprint = self.get_current_fingerprint()
                # if initial_fingerprint:
                #     self.print_fingerprint(initial_fingerprint, "Initial Fingerprint")

                return driver
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    print("Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    raise Exception("Failed to initialize WebDriver after multiple attempts")

    # def initialize_driver(self, max_retries):
        # ******************** Chrome Setup ********************
        # options = webdriver.ChromeOptions()
        # options.add_argument(f'--window-size={self.window_size[0]},{self.window_size[1]}')
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.add_experimental_option('useAutomationExtension', False)
        # options.add_argument(f'user-agent={self.ua.random}')
        # options.add_argument("--disable-blink-features=AutomationControlled")
        # options.add_argument("--start-maximized")
        # options.add_argument("--disable-extensions")
        # options.add_argument("--disable-popup-blocking")
        # options.add_argument('--no-sandbox')
        # options.add_argument('--disable-gpu')
        # options.add_argument('--disable-infobars')

        # # To enable incognito mode
        # options.add_argument("--incognito")

        # try:
        #     service = Service(r"C:\Program Files\chromedriver-win64\chromedriver.exe")
        #     self.driver = webdriver.Chrome(service=service, options=options)
        #     self.disable_webdriver_flags()
        #     self.logger.info(f"Initialized browser with User-Agent: {self.ua.random}")
        # except Exception as e:
        #     self.logger.error(f"Failed to initialize WebDriver: {e}")
        #     raise

        # ******************** Chrome Setup ********************
        # ******************** Firefox Setup ********************
        # options = FirefoxOptions()
        # options.add_argument('-private')  # This enables incognito mode in Firefox
        # options.add_argument(f'--width={self.window_size[0]}')
        # options.add_argument(f'--height={self.window_size[1]}')
        # options.set_preference("dom.webdriver.enabled", False)
        # options.set_preference('useAutomationExtension', False)
        # options.set_preference("general.useragent.override", self.ua.random)

        # try:
        #     service = FirefoxService(GeckoDriverManager().install())
        #     self.driver = webdriver.Firefox(service=service, options=options)
        #     self.driver.set_page_load_timeout(30)  # Set page load timeout here
        #     self.disable_webdriver_flags()
        #     self.logger.info(f"Initialized Firefox browser with User-Agent: {self.ua.random}")
        # except Exception as e:
        #     self.logger.error(f"Failed to initialize WebDriver: {e}")
        #     raise
        # ******************** Firefox Setup ********************


    def get_current_fingerprint(self):
        try:
            fingerprint = {
                "user_agent": self.driver.execute_script("return navigator.userAgent;"),
                "hardware_concurrency": self.driver.execute_script("return navigator.hardwareConcurrency;"),
                "device_memory": self.driver.execute_script("return navigator.deviceMemory;"),
                "webgl_vendor": self.driver.execute_script("var canvas = document.createElement('canvas'); var gl = canvas.getContext('webgl'); return gl.getParameter(gl.VENDOR);"),
                "webgl_renderer": self.driver.execute_script("var canvas = document.createElement('canvas'); var gl = canvas.getContext('webgl'); return gl.getParameter(gl.RENDERER);"),
                "languages": self.driver.execute_script("return navigator.languages;"),
                "plugins_length": self.driver.execute_script("return navigator.plugins.length;"),
                "screen_width": self.driver.execute_script("return screen.width;"),
                "screen_height": self.driver.execute_script("return screen.height;"),
            }
            return fingerprint
        except Exception as e:
            self.logger.error(f"Error getting current fingerprint: {e}")
            return None

    def print_fingerprint(self, fingerprint, message="Current Fingerprint"):
        self.logger.info(f"--- {message} ---")
        for key, value in fingerprint.items():
            self.logger.info(f"{key}: {value}")
        self.logger.info("-------------------")

    def verify_fingerprint(self):
        try:
            current_fingerprint = self.get_current_fingerprint()
            if current_fingerprint:
                self.print_fingerprint(current_fingerprint)
                
                # Check only critical fingerprint elements
                expected_ua = self.options.arguments[-1].split('=', 1)[1]
                if current_fingerprint['user_agent'] != expected_ua:
                    self.logger.warning(f"User agent mismatch. Expected: {expected_ua}, Actual: {current_fingerprint['user_agent']}")
                    return False
                
                # Add more lenient checks for other fingerprint elements if needed
            
            return True
        except Exception as e:
            self.logger.error(f"Error verifying fingerprint: {e}")
            return False

    def verify_user_agent(self):
        try:
            actual_user_agent = self.driver.execute_script("return navigator.userAgent;")
            expected_user_agent = self.options.arguments[-1].split('=', 1)[1]
            self.logger.info(f"Actual User Agent: {actual_user_agent}")
            if actual_user_agent != expected_user_agent:
                self.logger.warning(f"User agent mismatch. Expected: {expected_user_agent}, Actual: {actual_user_agent}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error verifying user agent: {e}")
            return False


    def disable_webdriver_flags(self, driver):
        try:
            driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            driver.execute_script("""
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """)
            driver.execute_script("""
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            """)
            # # Randomize navigator properties
            # driver.execute_script("""
            #     Object.defineProperty(navigator, 'hardwareConcurrency', {
            #         get: () => Math.floor(Math.random() * 8) + 2
            #     });
            #     Object.defineProperty(navigator, 'deviceMemory', {
            #         get: () => Math.pow(2, Math.floor(Math.random() * 4) + 1)
            #     });
            # """)
        except Exception as e:
            self.logger.error(f"Error disabling WebDriver flags: {e}")

    # # Randomize WebGL fingerprint
    #     try:
    #         driver.execute_script("""
    #             const getParameter = WebGLRenderingContext.prototype.getParameter;
    #             WebGLRenderingContext.prototype.getParameter = function(parameter) {
    #                 if (parameter === 37445) return 'Intel Open Source Technology Center';
    #                 if (parameter === 37446) return 'Mesa DRI Intel(R) HD Graphics (Skylake GT2)';
    #                 return getParameter.apply(this, arguments);
    #             };
    #         """)
    #     except Exception as e:
    #         self.logger.error(f"Error randomizing WebGL fingerprint: {e}")

    #     # After applying all changes, get and print the new fingerprint
    #     new_fingerprint = self.get_current_fingerprint()
    #     if new_fingerprint:
    #         self.print_fingerprint(new_fingerprint, "New Fingerprint After Disabling WebDriver Flags")


    def handle_stuck_situation(self):
        self.logger.warning("Detected a potentially stuck situation. Attempting to recover...")
        try:
            self.driver.execute_script("window.stop();")
            self.driver.get(self.main_url)
            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            self.logger.info("Successfully recovered from stuck situation")
        except Exception as e:
            self.logger.error(f"Failed to recover from stuck situation: {e}")
            self.reconnect_browser()


    def is_page_stuck(self):
        try:
            # Check if the page is still loading
            return self.driver.execute_script("return document.readyState") == "loading"
        except:
            # If we can't execute JavaScript, assume we're stuck
            return True

    
    # def disable_webdriver_flags(self):
    #     script = """
    #         Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    #         Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
    #         Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
    #     """
    #     self.driver.execute_script(script)


    def connect_vpn(self, location, max_retries=3):
        for attempt in range(max_retries):
            try:
                vpn_user = os.getenv('VPN_USER')
                vpn_pass = os.getenv('VPN_PASS')

                result = subprocess.run(["C:\\Program Files\\Windscribe\\windscribe-cli.exe", "status"], capture_output=True, text=True)
                if "DISCONNECTED" in result.stdout:
                    subprocess.run(["C:\\Program Files\\Windscribe\\windscribe-cli.exe", "login", vpn_user, vpn_pass], check=True)

                subprocess.run(["C:\\Program Files\\Windscribe\\windscribe-cli.exe", "connect", location], check=True, timeout=60)
                time.sleep(5)  # Wait for the connection to stabilize
                self.logger.info(f"Connected to WindScribe VPN {'server in ' + location if location else 'best'}")
                return True
            except subprocess.TimeoutExpired:
                self.logger.warning(f"VPN connection attempt {attempt + 1} timed out")
            except subprocess.CalledProcessError as e:
                self.logger.error(f"VPN connection attempt {attempt + 1} failed: {e}")
            
            if attempt < max_retries - 1:
                self.logger.info(f"Retrying VPN connection in 10 seconds...")
                time.sleep(10)
        
        self.logger.error("Failed to connect to VPN after multiple attempts")

        return False


    def disconnect_vpn(self):
        try:
            subprocess.run(["C:\\Program Files\\Windscribe\\windscribe-cli.exe", "disconnect"], check=True)
            self.logger.info(f"Disconnected from WindScribe VPN")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to disconnect from VPN: {e}")



    def wait_for_page_load(self, timeout=60):  # Increased timeout to 60 seconds
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            self.logger.info("Page loaded successfully")
            
            # Wait for AdSense scripts to load
            self.wait_for_adsense(timeout)
        except TimeoutException:
            self.logger.warning(f"Timeout waiting for page load after {timeout} seconds")
        except Exception as e:
            self.logger.error(f"Error waiting for page load: {e}")

    def wait_for_adsense(self, timeout=30):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ins.adsbygoogle"))
            )
            self.logger.info("AdSense scripts loaded successfully")
        except TimeoutException:
            self.logger.warning("Timeout waiting for AdSense scripts to load")
        except Exception as e:
            self.logger.error(f"Error waiting for AdSense scripts: {e}")

    def navigate_with_retry(self, url=None, max_retries=3):
        target_url = url or self.url
        self.logger.info(f"Attempting to navigate to: {target_url}")
        
        if not target_url:
            self.logger.error("No valid URL to navigate to.")
            return False
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Navigation attempt {attempt + 1}")
                self.driver.get(target_url)
                self.logger.info(f"Successfully loaded URL: {self.driver.current_url}")
                self.wait_for_page_load()
                self.handle_privacy_overlay()
                if target_url in self.driver.current_url:
                    self.logger.info(f"Successfully navigated to {target_url}")
                    return True
                else:
                    raise Exception("Navigation unsuccessful")
            except Exception as e:
                self.logger.error(f"Navigation attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    self.logger.error(f"Max retries reached. Navigation failed.")
                    return False
                time.sleep(random.uniform(5, 10))
        return False

    def take_screenshot(self, name):
        try:
            self.driver.save_screenshot(f"{name}.png")
            self.logger.info(f"Screenshot saved: {name}.png")
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}")

    # Define the highlightClick function in JavaScript
    def inject_highlight_script(self):
        highlight_script = """
        if (typeof window.highlightClick === 'undefined') {
            window.highlightClick = function(x, y) {
                var clickSpot = document.createElement('div');
                clickSpot.style.position = 'absolute';
                clickSpot.style.left = x + 'px';
                clickSpot.style.top = y + 'px';
                clickSpot.style.width = '20px';
                clickSpot.style.height = '20px';
                clickSpot.style.backgroundColor = 'red';
                clickSpot.style.borderRadius = '50%';
                clickSpot.style.opacity = '0.5';
                clickSpot.style.zIndex = '10000';
                document.body.appendChild(clickSpot);
                setTimeout(function() {
                    document.body.removeChild(clickSpot);
                }, 1000);
            };
        }
        if (typeof window.highlightScroll === 'undefined') {
            window.highlightScroll = function(y) {
                var scrollMarker = document.createElement('div');
                scrollMarker.style.position = 'absolute';
                scrollMarker.style.left = '0px';
                scrollMarker.style.top = y + 'px';
                scrollMarker.style.width = '100%';
                scrollMarker.style.height = '5px';
                scrollMarker.style.backgroundColor = 'blue';
                scrollMarker.style.opacity = '0.5';
                scrollMarker.style.zIndex = '10000';
                document.body.appendChild(scrollMarker);
                setTimeout(function() {
                    document.body.removeChild(scrollMarker);
                }, 1000);
            };
        }
        return true;  // Indicate successful injection
        """
        try:
            self.driver.execute_script(highlight_script)
            self.logger.info("Highlight script injected successfully")
        except Exception as e:
            self.logger.error(f"Failed to inject highlight script: {e}")
            return False

    # To use the highlightClick function, you would need to call the define_highlight_click method once when the page is loaded.
    # This would ensure that the function is available in the browser's console.
    # Once defined, you can use it to highlight and click elements on the page.

    def safe_click(self, element):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(random.uniform(0.5, 1))
            actions = ActionChains(self.driver)
            actions.move_to_element(element).perform()
            time.sleep(random.uniform(0.3, 0.7))
            rect = element.rect

            # Check if highlightClick is defined
            is_highlight_defined = self.driver.execute_script("return typeof highlightClick === 'function';")
            if not is_highlight_defined:
                self.logger.warning("highlightClick is not defined. Attempting to reinject the script.")
                if not self.inject_highlight_script():
                    self.logger.warning("Failed to reinject highlight script. Proceeding without highlighting.")
            
            if is_highlight_defined or self.inject_highlight_script():
                try:
                    self.driver.execute_script("highlightClick(arguments[0], arguments[1], arguments[2]);", rect['x'] + rect['width']/2, rect['y'] + rect['height']/2, 500)
                    # Script explanation: highlightClick(x, y, size)
                    # This script highlights a clickable area on the page by drawing a red box around it and then clicking the center of the box.
                    # It uses the scrollIntoView method to ensure the element is in view, then moves the mouse to the center of the element and performs a click.
                    # The highlightClick function is assumed to be a custom JavaScript function that performs these actions and is not defined in the provided code.
                    # To implement this, you would need to define the highlightClick function in JavaScript and ensure it is available in the browser's console.
                    # Here's an example of how you might define the highlightClick function in a JavaScript file:
                    # function highlightClick(x, y, size) {
                    #     var boxSize = size || 100;
                    #     var boxColor = "rgba(255, 0, 0, 0.5)";
                    #     var box = document.createElement("div");
                    #     box.style.position = "absolute";
                    #     box.style.left = (x - boxSize/2) + "px";
                    #     box.style.top = (y - boxSize/2) + "px";
                    #     box.style.width = boxSize + "px";
                    #     box.style.height = boxSize + "px";
                    #     box.style.border = "2px solid " + boxColor;
                    #     box.style.pointerEvents = "none";
                    #     document.body.appendChild(box);
                    #     setTimeout(function() {
                    #         document.body.removeChild(box);
                    #     }, 1000);
                    # }
                    # You would then include this JavaScript file in your HTML page or load it dynamically in your script.
                    # This script creates a temporary div element that is displayed as a red box around the clickable area.
                    # The box is removed after a short delay to ensure it doesn't interfere with other elements.
                    # You would need to ensure that this script is available in the browser's console when the page is loaded.
                except Exception as e:
                    self.logger.warning(f"Highlight click failed: {e}")
            element.click()
            return True
        except Exception as e:
            self.logger.error(f"Error clicking element: {e}")
            return False


    def get_css_selector(self, element):
        return element.tag_name + ''.join([f'[{attr}="{value}"]' for attr, value in element.get_property('attributes').items()])

    def safe_click_with_retry(self, element, max_retries=3):
        for attempt in range(max_retries):
            try:
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(element))
                
                # Check if highlightClick is defined
                is_highlight_defined = self.driver.execute_script("return typeof highlightClick === 'function';")
                if not is_highlight_defined:
                    self.logger.warning("highlightClick is not defined. Attempting to reinject the script.")
                    if not self.inject_highlight_script():
                        self.logger.warning("Failed to reinject highlight script. Proceeding without highlighting.")
                
                rect = element.rect
                click_points = [
                    (rect['x'] + rect['width'] * 0.2, rect['y'] + rect['height'] * 0.2),
                    (rect['x'] + rect['width'] * 0.8, rect['y'] + rect['height'] * 0.2),
                    (rect['x'] + rect['width'] * 0.2, rect['y'] + rect['height'] * 0.8),
                    (rect['x'] + rect['width'] * 0.8, rect['y'] + rect['height'] * 0.8),
                    (rect['x'] + rect['width'] * 0.5, rect['y'] + rect['height'] * 0.5)
                ]
                click_point = random.choice(click_points)
                
                if is_highlight_defined or self.inject_highlight_script():
                    try:
                        self.driver.execute_script("highlightClick(arguments[0], arguments[1], arguments[2]);", 
                                                   click_point[0], 
                                                   click_point[1], 
                                                   500)
                    except Exception as e:
                        self.logger.warning(f"Highlight click failed: {e}")
                
                # Hover on the element before clicking
                ActionChains(self.driver).move_to_element(element).perform()
                self.logger.info("Hovered on the element")
                
                # Try all click methods
                click_methods = [
                    lambda: element.click(),
                    lambda: self.driver.execute_script("arguments[0].click();", element),
                    lambda: ActionChains(self.driver).click().perform(),
                    lambda: ActionChains(self.driver).move_to_element_with_offset(element, click_point[0] - rect['x'], click_point[1] - rect['y']).click().perform(),
                    lambda: self.driver.execute_script(f"document.elementFromPoint({click_point[0]}, {click_point[1]}).click();")
                ]
                
                for method in click_methods:
                    try:
                        method()
                        self.logger.info(f"Successfully clicked element using method: {method.__name__}")
                        return True
                    except Exception as e:
                        self.logger.warning(f"Click method {method.__name__} failed: {e}")
                
                self.logger.error("All click methods failed.")
                return False
            
            except StaleElementReferenceException:
                if attempt == max_retries - 1:
                    self.logger.warning("Element became stale. Max retries reached.")
                    return False
                self.logger.info("Stale element reference. Retrying...")
            except Exception as e:
                self.logger.error(f"Error clicking element: {e}")
                return False
        return False


    def detect_and_handle_popups(self):
        try:
            # Check for alert
            try:
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                self.logger.info(f"Alert detected: {alert_text}")
                time.sleep(random.uniform(1, 2))
                alert.accept()
                self.logger.info("Alert accepted")
            except NoAlertPresentException:
                pass

            # Check for new windows
            original_handle = self.driver.current_window_handle
            for handle in self.driver.window_handles:
                if handle != original_handle:
                    self.driver.switch_to.window(handle)
                    self.logger.info(f"New window detected. Title: {self.driver.title}")
                    time.sleep(random.uniform(2, 3))
                    self.driver.close()
                    self.logger.info("Closed new window")
            self.driver.switch_to.window(original_handle)

            # Check for modal dialogs
            modal_selectors = [
                (By.CSS_SELECTOR, "div.modal, div.popup"),
                (By.XPATH, "//div[contains(@class, 'modal') or contains(@class, 'popup')]")
            ]
            for selector in modal_selectors:
                try:
                    modal = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(selector))
                    if modal.is_displayed():
                        close_button = modal.find_element(By.CSS_SELECTOR, "button.close, .close-button, [aria-label='Close']")
                        self.safe_click(close_button)
                        self.logger.info(f"Closed modal dialog: {selector}")
                except TimeoutException:
                    pass

            # Check for consent modal
            consent_modal_selectors = [
                (By.CSS_SELECTOR, "div[role='dialog']"),
                (By.XPATH, "//div[contains(@class, 'consent-modal')]"),
                (By.XPATH, "//div[contains(text(), 'consent') or contains(text(), 'Consent')]")
            ]
            for selector in consent_modal_selectors:
                try:
                    modal = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(selector))
                    if modal.is_displayed():
                        self.handle_consent_modal()
                        break
                except TimeoutException:
                    pass

        except Exception as e:
            self.logger.error(f"Error handling popups: {e}")

    def is_post_page(self):
        post_indicators = ['article', 'div.post-content', 'div.entry-content']
        url_contains_post = '/post/' in self.driver.current_url
        return url_contains_post or any(self.driver.find_elements(By.CSS_SELECTOR, indicator) for indicator in post_indicators)

    def simulate_human_behavior(self):
        base_actions = [
            self.random_scroll,
            self.random_mouse_movement,
            self.click_random_link
        ]
        
        for _ in range(random.randint(3, 5)):
            actions = base_actions.copy()
            
            chosen_action = random.choice(actions)
            self.logger.info(f"▶▶▶ PERFORMING ACTION: {chosen_action.__name__.upper()} ◀◀◀")
            try:
                chosen_action()
                self.handle_ad_support_modal()
                
                if self.is_post_page():
                    self.logger.info("▶▶▶ PERFORMING ACTION: READ_ARTICLE ◀◀◀")
                    self.read_article()
            except Exception as e:
                self.logger.error(f"Error during {chosen_action.__name__}: {e}")
            time.sleep(random.uniform(0.5, 1.5))

    def random_scroll(self):
        scroll_length = random.randint(100, 500)
        self.driver.execute_script(f"window.scrollBy(0, {scroll_length}); highlightScroll();")
        self.logger.info(f"ACTION: Random scroll by {scroll_length}px")
        time.sleep(random.uniform(1, 3))

    def highlight_element(self, element, duration=2):
        original_style = element.get_attribute('style')
        self.driver.execute_script("""
            var element = arguments[0];
            element.style.border = '5px solid red';
            element.style.backgroundColor = 'yellow';
        """, element)
        # self.take_screenshot(f"highlight_{element.tag_name}")
        time.sleep(duration)
        self.driver.execute_script(f"arguments[0].setAttribute('style', '{original_style}');", element)

    def random_mouse_movement(self):
        try:
            actions = ActionChains(self.driver)
            viewport_width = self.driver.execute_script("return Math.min(window.innerWidth, document.documentElement.clientWidth);")
            viewport_height = self.driver.execute_script("return Math.min(window.innerHeight, document.documentElement.clientHeight);")
            
            elements = self.driver.find_elements(By.XPATH, "//*[not(self::script) and not(self::style)]")
            current_x, current_y = 0, 0
            for _ in range(random.randint(3, 7)):
                target_x = random.randint(0, viewport_width - 1)
                target_y = random.randint(0, viewport_height - 1)
                
                # Simulate human-like movement with bezier curve
                points = self.bezier_curve(current_x, current_y, target_x, target_y)
                for point in points:
                    actions.move_by_offset(point[0] - current_x, point[1] - current_y)
                    current_x, current_y = point
                    actions.pause(random.uniform(0.01, 0.03))
                
                # Pause at the target point
                actions.pause(random.uniform(0.1, 0.3))

                element = random.choice(elements)
                if element.is_displayed():
                    self.highlight_element(element)
                    print(f"Highlighted element: {element.tag_name}")
            
            actions.perform()
            self.logger.info("Performed random element highlights")
            self.logger.info(f"Performed random mouse movements within viewport ({viewport_width}x{viewport_height})")
        except Exception as e:
            self.logger.error(f"Error during mouse movement: {e}")

    def bezier_curve(self, x1, y1, x2, y2, num_points=20):
        # Generate control points
        cx1, cy1 = x1 + random.randint(50, 100), y1 + random.randint(-50, 50)
        cx2, cy2 = x2 - random.randint(50, 100), y2 + random.randint(-50, 50)
        
        # Generate points along the bezier curve
        points = []
        for t in [i / (num_points - 1) for i in range(num_points)]:
            x = (1-t)**3 * x1 + 3*(1-t)**2 * t * cx1 + 3*(1-t) * t**2 * cx2 + t**3 * x2
            y = (1-t)**3 * y1 + 3*(1-t)**2 * t * cy1 + 3*(1-t) * t**2 * cy2 + t**3 * y2
            points.append((int(x), int(y)))
        return points

    def click_random_link(self):
        try:
            links = self.driver.find_elements(By.TAG_NAME, 'a')
            visible_links = [link for link in links if link.is_displayed()]
            if visible_links:
                random_link = random.choice(visible_links)
                href = random_link.get_attribute('href')
                if href:
                    if href.startswith(self.main_url) or random.random() < 0.2:  # 20% chance to click external links
                        # Verify link hover before clicking
                        if self.verify_link_hover(random_link):
                            actions = ActionChains(self.driver)
                            actions.move_to_element(random_link).click().perform()
                            self.logger.info(f"ACTION: Clicked random link - {href}")
                            if not href.startswith(self.main_url):
                                time.sleep(3)
                                self.driver.back()
                            return True
                        else:
                            self.logger.info(f"Skipped link due to hover verification failure")
                    else:
                        self.logger.info(f"Skipped external link")
                else:
                    self.logger.info(f"Skipped link with no href")
            else:
                self.logger.info(f"No visible links found on the page")
        except Exception as e:
            self.logger.error(f"Error clicking random link: {e}")
        return False

    def read_article(self):
        try:
            # Check if we're on a post page
            post_indicators = ['article', 'div.post-content', 'div.entry-content']
            is_post_page = any(self.driver.find_elements(By.CSS_SELECTOR, indicator) for indicator in post_indicators)
            
            if is_post_page:
                content_selectors = post_indicators + ['div.content', 'main', 'div.main-content']
                for selector in content_selectors:
                    try:
                        content = self.driver.find_element(By.CSS_SELECTOR, selector)
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'start'});", content)
                        time.sleep(random.uniform(1, 2))
                        content_height = content.size['height']
                        viewport_height = self.driver.execute_script("return window.innerHeight")
                        scroll_amount = 0
                        while scroll_amount < content_height:
                            scroll_step = random.randint(50, 150)
                            self.driver.execute_script(f"window.scrollBy(0, {scroll_step});")
                            scroll_amount += scroll_step
                            time.sleep(random.uniform(0.5, 1.5))
                        self.logger.info(f"ACTION: Read article with selector: {selector}")
                        return
                    except NoSuchElementException:
                        continue
                self.logger.warning(f"No article content found on the post page")
            else:
                self.random_human_like_scroll()
                self.logger.info(f"ACTION: Performed random human-like scroll on non-post page")
        except Exception as e:
            self.logger.error(f"Error reading article: {e}")

    def random_human_like_scroll(self):
        try:
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            max_scroll = total_height - viewport_height
            
            scroll_amount = 0
            while scroll_amount < max_scroll:
                scroll_step = random.randint(100, 300)
                scroll_amount += scroll_step
                self.driver.execute_script(f"window.scrollTo(0, {min(scroll_amount, max_scroll)});")
                time.sleep(random.uniform(0.5, 2))
                
                # Occasionally scroll up a bit
                if random.random() < 0.2:
                    up_scroll = random.randint(50, 100)
                    scroll_amount -= up_scroll
                    self.driver.execute_script(f"window.scrollTo(0, {max(0, scroll_amount)});")
                    time.sleep(random.uniform(0.5, 1))
            
            # Scroll back to top
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            self.logger.error(f"Error during random human-like scroll: {e}")

    def find_and_interact_with_ads(self):
        ad_selectors = [
            (By.CSS_SELECTOR, "ins.adsbygoogle"),
            (By.CSS_SELECTOR, "iframe[src*='googleadservices']"),
            (By.CSS_SELECTOR, "div[id^='google_ads_iframe']"),
            (By.XPATH, "//iframe[contains(@id, 'google_ads_iframe')]"),
            (By.CSS_SELECTOR, "div[id^='ad-']"),
            (By.CSS_SELECTOR, "div[class*='ad-']"),
            (By.CSS_SELECTOR, "div[class*='advertisement']"),
            ('css selector', 'ins.adsbygoogle'),
            ('css selector', 'div[id^="div-gpt-ad"]'),
            ('xpath', '//iframe[contains(@id, "google_ads_iframe")]')
        ]
        
        ads_found = []
        for selector in ad_selectors:
            try:
                ads = self.driver.find_elements(*selector)
                for ad in ads:
                    if ad.is_displayed():
                        ads_found.append(ad)
            except Exception as e:
                self.logger.warning(f"Error finding ads with selector {selector}: {e}")
        
        self.logger.info(f"Found {len(ads_found)} visible ads")
        
        for ad in ads_found:
            try:
                self.interact_with_ad(ad)
            except Exception as e:
                self.logger.error(f"Error interacting with ad: {e}")

    def interact_with_ad(self, ad):
        try:
            self.scroll_to_element(ad)
            time.sleep(random.uniform(0.5, 1))
            
            if random.random() < 0.5:  # 50% chance of interacting
                if ad.tag_name == "iframe":
                    self.driver.switch_to.frame(ad)
                
                clickable = self.find_clickable_element(ad)
                if clickable:
                    self.safe_click(clickable)
                    self.logger.info(f"Clicked on ad: {ad.get_attribute('outerHTML')[:100]}...")
                    self.handle_new_tab()
                else:
                    self.logger.info(f"No clickable element found within the ad")
                
                if ad.tag_name == "iframe":
                    self.driver.switch_to.default_content()
        except Exception as e:
            self.logger.error(f"Error interacting with ad: {e}")


    def switch_to_iframe_and_handle_vignette(self):
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
            for iframe in iframes:
                try:
                    self.driver.switch_to.frame(iframe)
                    vignette = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.vignette"))
                    )
                    if vignette.is_displayed():
                        close_button = self.driver.find_element(By.CSS_SELECTOR, "button.close-button")
                        close_button.click()
                        self.logger.info(f"Closed vignette overlay")
                    self.driver.switch_to.default_content()
                except TimeoutException:
                    self.driver.switch_to.default_content()
                    continue
                except Exception as e:
                    self.logger.error(f"Error handling vignette in iframe: {e}")
                    self.driver.switch_to.default_content()
        except Exception as e:
            self.logger.error(f"Error switching to iframe: {e}")


# def handle_google_vignette(self):
    #     try:
    #         # Try to find and click the full screen overlay ad
    #         overlay = WebDriverWait(self.driver, 10).until(
    #             EC.presence_of_element_located((By.CSS_SELECTOR, "div.google-vignette-overlay"))
    #         )
    #         self.safe_click(overlay)
    #         self.logger.info("Clicked on Google Vignette overlay")
    #         time.sleep(2)  # Wait for any action to complete

    #         # If clicking doesn't work, try to close it
    #         close_button = self.driver.find_element(By.CSS_SELECTOR, "div.google-vignette-close-button")
    #         if close_button:
    #             self.safe_click(close_button)
    #             self.logger.info("Closed Google Vignette overlay")
    #             time.sleep(2)

    #         # If all else fails, return to the main URL
    #         if "#google_vignette" in self.driver.current_url:
    #             self.driver.get(f"{self.main_url}")
    #             self.wait_for_page_load()
    #             self.logger.info("Returned to main URL to bypass Google Vignette")

    #     except Exception as e:
    #         self.logger.error(f"Error handling Google Vignette: {e}")
    #         # If we can't handle it, return to the main URL
    #         self.driver.get(f"{self.main_url}")
    #         self.wait_for_page_load()
    #         self.logger.info("Returned to main URL after failing to handle Google Vignette")

    
    def handle_google_vignette(self):
        try:
            overlay_selectors = [
                "div[id^='google_ads_iframe'][style*='position: fixed']",
                "iframe[id^='google_ads_iframe'][style*='position: fixed']",
                "div[id^='google_vignette']",
                "div[class*='google-vignette']",
                "div[class*='vignette-container']"
            ]
            
            for selector in overlay_selectors:
                try:
                    overlay = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if overlay.is_displayed() and overlay.size['height'] > self.driver.execute_script("return window.innerHeight") * 0.5:
                        self.logger.info(f"Full-screen overlay ad detected using selector: {selector}")
                        
                        # Try to click the ad first
                        if self.click_ad(overlay):
                            return True
                        
                        # If clicking the ad didn't work, try to close it
                        if self.close_overlay_ad(overlay):
                            return True
                        
                        # If no close button found, try to click outside the ad
                        self.click_outside_ad()
                        
                        # If the ad is still present, try to remove it using JavaScript
                        if self.remove_overlay_using_javascript():
                            return True
                        
                except TimeoutException:
                    continue
            
            self.logger.info("No overlay ad detected or unable to interact with it")
            return False
        except Exception as e:
            self.logger.error(f"Error handling overlay ad: {e}")
            return False

    def click_ad(self, overlay):
        try:
            clickable = self.find_all_clickable_elements(overlay)
            if clickable:
                self.safe_click_with_retry(clickable)
                self.logger.info(f"Clicked on ad or clickable element within the ad")
                time.sleep(2)
                return True
            else:
                self.safe_click_with_retry(overlay)
                self.logger.info(f"Clicked on the overlay itself")
                time.sleep(2)
                return True
        except Exception as e:
            self.logger.error(f"Error clicking on ad: {e}")
            return False

    def close_overlay_ad(self, overlay):
        close_button_selectors = [
            "button[aria-label='Close ad']", ".close-button", "#dismiss-button",
            "div[aria-label='Close ad']", "div[role='button'][aria-label='Close']",
            "span[aria-label='Close']", "img[alt='close button']",
            "span[class*='close']", "div[class*='close']",
            "[class*='dismiss']", "[id*='dismiss']"
        ]
        
        for close_selector in close_button_selectors:
            try:
                close_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, close_selector))
                )
                self.driver.execute_script("arguments[0].click();", close_button)
                self.safe_click(close_button)
                self.logger.info(f"Clicked close button on full-screen overlay ad using selector: {close_selector}")
                time.sleep(2)
                return True
            except:
                continue
        return False

    def click_outside_ad(self):
        actions = ActionChains(self.driver)
        actions.move_by_offset(-50, -50).click().perform()
        self.logger.info("Attempted to close overlay ad by clicking outside")
        time.sleep(2)

    def remove_overlay_using_javascript(self):
        self.driver.execute_script("""
            var elements = document.querySelectorAll('div[style*="position: fixed"], div[class*="overlay"], div[class*="modal"]');
            for(var i=0; i<elements.length; i++){
                elements[i].parentNode.removeChild(elements[i]);
            }
        """)
        self.logger.info("Attempted to remove overlay ad using JavaScript")
        time.sleep(2)
        
        # Check if the overlay is still present
        try:
            overlay = self.driver.find_element(By.CSS_SELECTOR, self.current_selector)
            if not overlay.is_displayed():
                self.logger.info("Overlay ad removed successfully")
                return True
        except:
            self.logger.info("Overlay ad removed successfully")
            return True
        
        return False
    
    def reconnect_browser(self):
        self.logger.info(f"Browser connection lost. Attempting to reconnect...")
        try:
            self.driver.quit()
        except:
            pass
        self.driver = self.initialize_driver(max_retries=3)
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.get(self.main_url)
        self.logger.info(f"Reconnected to the browser.")

    def verify_link_hover(self, element):
        try:
            actions = ActionChains(self.driver)
            actions.move_to_element(element).perform()
            self.driver.execute_script("highlightHover(arguments[0]);", element)
            time.sleep(1)
            self.logger.info(f"Hovered over link: {element.get_attribute('href')}")
            return True
        except Exception as e:
            self.logger.error(f"Error during link hover: {e}")
            return False

    def handle_privacy_overlay(self):
        try:
            overlay = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "privacy-overlay"))
            )
            close_button = overlay.find_element(By.XPATH, ".//button[contains(@class, 'close') or contains(text(), 'Accept')]")
            self.safe_click(close_button)
            self.logger.info(f"Closed privacy overlay")
        except (TimeoutException, NoSuchElementException):
            self.logger.info(f"No privacy overlay found or already closed")


    def handle_consent_modal(self):
        try:
            # Wait for the consent modal to appear
            consent_modal = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='dialog']"))
            )
            self.logger.info("Consent modal detected")

            # Try different methods to find the consent button
            consent_button_selectors = [
                (By.XPATH, "//button[contains(text(), 'Consent')]"),
                (By.XPATH, "//button[contains(@class, 'consent')]"),
                (By.CSS_SELECTOR, "button.consent-button"),
                (By.CSS_SELECTOR, "button[data-testid='consent-button']"),
                (By.XPATH, "//button[normalize-space()='Consent']"),
                (By.XPATH, "//button[@aria-label='Consent']"),
                (By.XPATH, "//button[@aria-label='Accept']"),
                (By.XPATH, "//button[@aria-label='Agree']")
            ]

            for selector in consent_button_selectors:
                try:
                    consent_button = WebDriverWait(consent_modal, 5).until(
                        EC.element_to_be_clickable(selector)
                    )
                    self.safe_click(consent_button)
                    self.logger.info(f"Clicked 'Consent' button using selector: {selector}")
                    break
                except TimeoutException:
                    continue

            # Wait for the modal to disappear
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, "div[role='dialog']"))
            )
            self.logger.info("Consent modal closed successfully")
        except TimeoutException:
            self.logger.info("No consent modal found or already closed")
        except Exception as e:
            self.logger.error(f"Error handling consent modal: {e}")
            # If we can't handle the modal, try to continue anyway
            pass


    def handle_ad_support_modal(self):
        try:
            # Wait for the modal to appear (adjust the timeout as needed)
            modal = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "adSupportModal"))
            )
            print("Ad Support Modal found")

            # Find and click the "Got it, thanks!" button
            close_button = modal.find_element(By.XPATH, "//button[contains(text(), 'Got it, thanks!')]")
            close_button.click()
            print("Clicked 'Got it, thanks!' button on Ad Support Modal")

            # Wait for the modal to disappear
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located((By.ID, "adSupportModal"))
            )
            print("Ad Support Modal closed successfully")
        except TimeoutException:
            print("Ad Support Modal not found or already closed")
        except Exception as e:
            print(f"Error handling Ad Support Modal: {e}")

    
    def scroll_and_navigate(self):
        total_height = self.driver.execute_script("return document.body.scrollHeight")
        viewport_height = self.driver.execute_script("return window.innerHeight")
        scroll_steps = random.randint(3, 7)
        
        for _ in range(scroll_steps):
            scroll_y = random.randint(viewport_height, total_height - viewport_height)
            self.driver.execute_script(f"window.scrollTo(0, {scroll_y});")
            self.driver.execute_script(f"highlightScroll({scroll_y});")
            time.sleep(random.uniform(1, 3))
        
        # Navigate to a random internal link
        internal_links = self.driver.find_elements(By.XPATH, f"//a[starts-with(@href, '/') or starts-with(@href, '{self.main_url}')]")
        if internal_links:
            random_link = random.choice(internal_links)
            self.safe_click(random_link)
            self.wait_for_page_load()


    def print_progress(self):
        if self.start_time is None:
            return

        current_time = time.time()
        elapsed_time = current_time - self.start_time
        elapsed_str = str(timedelta(seconds=int(elapsed_time)))

        if self.total_ads_clicked > 0:
            ads_per_second = self.total_ads_clicked / elapsed_time
            estimated_total_time = self.max_ads_to_click / ads_per_second
            estimated_remaining_time = max(0, estimated_total_time - elapsed_time)
            estimated_remaining_str = str(timedelta(seconds=int(estimated_remaining_time)))
        else:
            estimated_remaining_str = "Unknown"

        progress_percentage = (self.total_ads_clicked / self.max_ads_to_click) * 100
        progress_bar = '█' * int(progress_percentage // 2) + '░' * (50 - int(progress_percentage // 2))

        def format_time(time_str):
            parts = time_str.split(':')
            if len(parts) == 3:
                return f"{int(parts[0]):02d}h {int(parts[1]):02d}m {int(parts[2]):02d}s"
            elif len(parts) == 2:
                return f"{int(parts[0]):02d}m {int(parts[1]):02d}s"
            else:
                return f"{int(parts[0]):02d}s"

        elapsed_formatted = format_time(elapsed_str)
        estimated_remaining_formatted = format_time(estimated_remaining_str) if estimated_remaining_str != "Unknown" else "Unknown"

        # Example of how it will be displayed:
        # ┌──────────────────────────────────────────────────────────────────────────────┐
        # │ Progress: [██████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░] 52.0%         │
        # │ Ads Clicked: 26/50                                                           │
        # │ Elapsed Time: 00h 15m 30s                                                    │
        # │ Estimated Remaining: 00h 14m 20s                                             │
        # └──────────────────────────────────────────────────────────────────────────────┘

        print(f"\r┌{'─' * 78}┐\n"
              f"│ Progress: [{progress_bar}] {progress_percentage:.1f}%{' ' * (17 - len(f'{progress_percentage:.1f}'))}│\n"
              f"│ Ads Clicked: {self.total_ads_clicked}/{self.max_ads_to_click}{' ' * (54 - len(str(self.total_ads_clicked)) - len(str(self.max_ads_to_click)))}│\n"
              f"│ Elapsed Time: {elapsed_formatted}{' ' * (62 - len(elapsed_formatted))}│\n"
              f"│ Estimated Remaining: {estimated_remaining_formatted}{' ' * (54 - len(estimated_remaining_formatted))}│\n"
              f"└{'─' * 78}┘\n", end="", flush=True)


    def click_ad_content(self):
        try:
            ad_selectors = [
                (By.CSS_SELECTOR, "ins.adsbygoogle"),
                (By.CSS_SELECTOR, "iframe[src*='googleadservices']"),
                (By.CSS_SELECTOR, "div[id^='google_ads_iframe']"),
                (By.XPATH, "//iframe[contains(@id, 'google_ads_iframe')]"),
                (By.CSS_SELECTOR, "div[id^='ad-']"),
                (By.CSS_SELECTOR, "div[class*='ad-']"),
                (By.CSS_SELECTOR, "div[class*='advertisement']"),
                ('css selector', 'ins.adsbygoogle'),
                ('css selector', 'div[id^="div-gpt-ad"]'),
                ('xpath', '//iframe[contains(@id, "google_ads_iframe")]')
            ]


            all_ad_elements = []
            
            for selector in ad_selectors:
                ad_elements = self.driver.find_elements(*selector)
                all_ad_elements.extend([(ad, selector) for ad in ad_elements])
            
            self.logger.info(f"Found {len(all_ad_elements)} potential ad elements")

            # Shuffle the list of ad elements
            random.shuffle(all_ad_elements)

            visible_ads_found = False
            
            for ad_element, selector in all_ad_elements:
                ad_identifier = f"{selector}_{ad_element.location['x']}_{ad_element.location['y']}"

                if ad_identifier not in self.clicked_ads:
                    if ad_element.is_displayed() and ad_element.size['height'] > 0 and ad_element.size['width'] > 0:
                        visible_ads_found = True
                        self.logger.info(f"Found unclicked visible ad: {selector}")
                        
                        # Scroll to the ad
                        self.scroll_to_element(ad_element)
                        time.sleep(random.uniform(0.5, 1))  # Reduced wait time
                    
                        self.highlight_element(ad_element)
                        self.logger.info(f"Highlighted ad: {selector}")

                        # Check for #google_vignette in URL
                        # This code will be executed after all potential ad elements have been processed.
                        # If no clickable ad content is found, it will check if the current URL contains #google_vignette
                        # and attempt to close it or navigate back to the main URL.
                        
                        if "#google_vignette" in self.driver.current_url:
                            self.logger.info("Detected #google_vignette in URL, attempting to close it")
                            try:
                                close_button = self.driver.find_element(By.CSS_SELECTOR, "div[role='button'][aria-label='Close']")
                                if close_button.is_displayed():
                                    close_button.click()
                                    self.logger.info("Closed #google_vignette ad")
                                    return True
                                
                                self.logger.info("No close button found for #google_vignette ad")
                                self.logger.info("Attempting to find all clickable elements to close #google_vignette ad")
                                
                                clickable_elements = self.find_all_clickable_elements(self.driver.find_element(By.TAG_NAME, 'body'))
                                for element in clickable_elements:
                                    try:
                                        self.highlight_element(element)
                                        if self.safe_click_with_retry(element):
                                            self.logger.info("Clicked on a clickable element to close #google_vignette ad")
                                            return True
                                    except Exception as e:
                                        self.logger.error(f"Error clicking element to close #google_vignette ad: {e}")
                                

                                vignette_handled = self.handle_google_vignette()
                                if not vignette_handled:
                                    self.logger.warning("Unable to handle Google Vignette. Refreshing the page...")
                                    self.driver.refresh()
                                    self.wait_for_page_load()
                                    return True

                                self.logger.info("Detected #google_vignette in URL, returning to main URL")
                                self.driver.get(self.main_url)
                                self.wait_for_page_load()
                                self.logger.info("Returned to main URL to bypass Google Vignette")

                                return True
                            except Exception as e:
                                self.logger.error(f"Error closing #google_vignette ad: {e}")

                        
                        # # # Simulate hover
                        # actions = ActionChains(self.driver)
                        # actions.move_to_element(ad_element).perform()
                        # time.sleep(random.uniform(0.5, 1))

                        # Switch to iframe if the ad is an iframe
                        if ad_element.tag_name == 'iframe':
                            try:
                                self.driver.switch_to.frame(ad_element)
                                clickable_elements = self.find_all_clickable_elements(self.driver.find_element(By.TAG_NAME, 'body'))
                                self.driver.switch_to.default_content()
                            except Exception as e:
                                self.logger.error(f"Error switching to iframe: {e}")
                                self.driver.switch_to.default_content()
                                clickable_elements = []
                        else:
                            clickable_elements = self.find_all_clickable_elements(ad_element)
                        
                        self.logger.info(f"Found {len(clickable_elements)} clickable elements within the ad")

                        if clickable_elements:
                            clickable = random.choice(clickable_elements)
                            current_url = self.driver.current_url
                            original_handles = self.driver.window_handles

                            try:
                                self.highlight_element(clickable)
                                self.logger.info(f"Highlighted clickable element within ad: {clickable.tag_name}")

                                if self.safe_click_with_retry(clickable):
                                    # actions = ActionChains(self.driver)
                                    # actions.move_to_element(clickable).pause(1).click().perform()
                                    # self.logger.info(f"Clicked on element within ad: {clickable.tag_name}")
                                    # time.sleep(2)

                                    # # Use JavaScript to click the element
                                    # self.driver.execute_script("arguments[0].click();", clickable)
                                    # self.logger.info(f"Clicked on element within ad using JavaScript: {clickable.tag_name}")
                                    # time.sleep(2)

                                    if self.driver.current_url != current_url:
                                        self.clicked_ads.add(ad_identifier)
                                        self.total_ads_clicked += 1
                                        self.logger.info(f"Successfully clicked ad. Total ads clicked: {self.total_ads_clicked}")
                                        return True
                                    else:
                                        new_handles = self.driver.window_handles
                                        if len(new_handles) > len(original_handles):
                                            self.logger.info("New tab opened after ad click")
                                            self.clicked_ads.add(ad_identifier)
                                            self.total_ads_clicked += 1
                                            self.driver.switch_to.window(new_handles[-1])  # Switch to the new tab
                                            time.sleep(1)  # Wait for the new page to load
                                            self.driver.close()  # Close the new tab
                                            self.driver.switch_to.window(original_handles[0])  # Switch back to the original tab
                                            return True
                                        else:
                                            self.logger.info("Ad click did not result in page change or new tab, trying next ad")
                                    
                            except Exception as click_error:
                                self.logger.error(f"Error clicking ad element: {click_error}")
                        else:
                            self.logger.info("No clickable element found within the ad")
                        
                        # Switch back to default content if we were in an iframe
                        if ad_element.tag_name == 'iframe':
                            self.driver.switch_to.default_content()
                            self.logger.info("Switched back to default content")
                    else:
                        self.logger.info(f"Ad not visible or has zero dimensions: {selector}")
                else:
                    self.logger.info(f"Ad already clicked: {selector}")

            if not visible_ads_found:
                self.logger.info("No visible ads found, refreshing the page...")
                self.driver.refresh()
                self.wait_for_page_load()

            self.logger.info("No clickable ad content found")
            return False
        except Exception as e:
            self.logger.error(f"Error interacting with ad content: {e}")
            return False


    def search_and_click_ads(self):
        ads_clicked_this_session = 0
        max_attempts = 5
        attempts = 0
        consecutive_failures = 0
        target_ad_clicks = self.max_ads_to_click

        last_print_time = self.start_time
        while ads_clicked_this_session < target_ad_clicks and attempts < max_attempts and consecutive_failures < 3:

            # Print progress every 5 seconds
            current_time = time.time()
            if current_time - last_print_time >= 5:
                self.print_progress()
                last_print_time = current_time

            self.logger.info(f"Ad search attempt {attempts + 1}/{max_attempts}")
            original_url = self.driver.current_url
            original_handle = self.driver.current_window_handle

            if self.main_url not in original_url:
                self.logger.info(f"Current URL {original_url} is not part of main site. Navigating back to main site.")
                self.navigate_with_retry(self.main_url)
                continue

            try:
                if self.click_ad_content():
                    ads_clicked_this_session += 1
                    consecutive_failures = 0
                    self.logger.info(f"Clicked ad {self.total_ads_clicked} on page: {original_url}")
                    
                    self.handle_new_tab(original_handle)
                    
                    self.driver.switch_to.window(original_handle)
                    if self.driver.current_url != original_url:
                        self.navigate_with_retry(original_url)
                    
                    self.logger.info(f"Returned to original page: {original_url}")
                else:
                    consecutive_failures += 1
                    self.logger.info(f"No clickable ads found on page: {self.driver.current_url}. Consecutive failures: {consecutive_failures}")
                    self.navigate_to_random_page()  # Always navigate to a new page
            except TimeoutException:
                self.logger.warning("Timeout occurred. Navigating to a new page.")
                self.navigate_to_random_page()
            except Exception as e:
                self.logger.error(f"Error during ad search: {e}")
                consecutive_failures += 1
            
            attempts += 1
            self.logger.info(f"Current ad click count: {self.total_ads_clicked}")

        if consecutive_failures >= 3:
            self.logger.warning("Stopped due to too many consecutive failures to find clickable ads")

        self.logger.info(f"Total ads clicked in this session: {ads_clicked_this_session}")
        self.logger.info(f"Total ads clicked overall: {self.total_ads_clicked}")

        # Print final progress for this search_and_click_ads session
        self.print_progress()

        return ads_clicked_this_session


    def find_clickable_element(self, element):
        try:
            # List of clickable_selectors for potentially clickable elements
            clickable_selectors = [
                "a", "button", "[role='button']", "[tabindex='0']",
                "h1", "h2", "h3", "h4", "h5", "h6",  # Headings
                "p", "span", "div",  # Text elements
                "img", "svg",  # Images and SVGs
                "[onclick]", "[class*='clickable']", "[class*='button']",  # Elements with click-related attributes
                "[data-click]", "[data-href]",  # Custom data attributes
                "input[type='submit']", "input[type='button']"  # Form inputs
            ]
            
            # Join all clickable_selectors
            selector_string = ', '.join(clickable_selectors)
            
            # Find all potential clickable elements
            clickable_elements = element.find_elements(By.CSS_SELECTOR, selector_string)
            
            # Filter visible elements
            visible_elements = [el for el in clickable_elements if el.is_displayed() and el.is_enabled()]
            
            if visible_elements:
                # Prioritize elements that are more likely to be clickable
                for el in visible_elements:
                    if el.tag_name in ['a', 'button'] or el.get_attribute('role') == 'button':
                        return el
                
                # If no priority elements found, return the first visible element
                return visible_elements[0]
            
            return None
        except NoSuchElementException:
            return None


    def find_all_clickable_elements(self, element):
        try:
            clickable_selectors = [
                "a", "button", "[role='button']", "[tabindex='0']",
                "h1", "h2", "h3", "h4", "h5", "h6",
                "p", "span", "div",
                "img", "svg",
                "[onclick]", "[class*='clickable']", "[class*='button']",
                "[data-click]", "[data-href]",
                "input[type='submit']", "input[type='button']",
                # Add more specific ad-related selectors
                "[class*='ad-title']", "[class*='ad-description']",
                "[class*='sponsored']", "[class*='promotion']",
                "[id*='ad-title']", "[id*='ad-description']",
                "[aria-label*='advertisement']", "[aria-label*='sponsored']"
            ]
            
            selector_string = ', '.join(clickable_selectors)
            all_elements = element.find_elements(By.CSS_SELECTOR, selector_string)
            
            return [el for el in all_elements if el.is_displayed() and el.is_enabled()]
        except Exception:
            return []

    def scroll_to_element(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)


    def find_clickable_element_in_frame(self):
        try:
            # List of selectors for potentially clickable elements
            selectors = [
                "a", "button", "[role='button']", "[tabindex='0']",
                "h1", "h2", "h3", "h4", "h5", "h6",  # Headings
                "p", "span", "div",  # Text elements
                "img", "svg",  # Images and SVGs
                "[onclick]", "[class*='clickable']", "[class*='button']",  # Elements with click-related attributes
                "[data-click]", "[data-href]",  # Custom data attributes
                "input[type='submit']", "input[type='button']"  # Form inputs
            ]
            
            # Join all selectors
            selector_string = ', '.join(selectors)
            
            # Wait for any of these elements to be clickable
            clickable = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector_string))
            )
            return clickable
        except TimeoutException:
            return None

    def handle_new_tab(self, original_handle):
        try:
            new_handles = [handle for handle in self.driver.window_handles if handle != original_handle]
            if new_handles:
                self.logger.info("New tab opened after ad click")
                for new_handle in new_handles:
                    self.driver.switch_to.window(new_handle)
                    
                    # Set a short page load timeout
                    self.driver.set_page_load_timeout(5)
                    
                    try:
                        # Try to get the URL, but don't wait for full page load
                        url = self.driver.current_url
                        self.logger.info(f"Switched to new tab: {url}")
                    except:
                        self.logger.info("Switched to new tab, but couldn't get URL")
                    
                    # Quick interaction with the new tab
                    interaction_time = random.uniform(1, 3)
                    self.logger.info(f"Interacting with new tab for {interaction_time:.2f} seconds")
                    
                    # Perform a quick scroll
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.3);")
                    
                    time.sleep(interaction_time)
                    
                    # Close the new tab
                    self.driver.close()
                    self.logger.info("Closed new tab")
                
                # Switch back to the original tab
                self.driver.switch_to.window(original_handle)
            else:
                self.logger.info("No new tab opened after ad click")
        except Exception as e:
            self.logger.error(f"Error handling new tab: {e}")
        finally:
            # Ensure we switch back to the original handle even if an error occurs
            self.driver.switch_to.window(original_handle)
            # Reset page load timeout to default
            self.driver.set_page_load_timeout(30)

    # def navigate_to_post(self):
    #     try:
    #         # Find all post links on the current page
    #         post_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/post/')]")
    #         if post_links:
    #             random_post = random.choice(post_links)
    #             self.safe_click(random_post)
    #             self.wait_for_page_load()
    #             self.logger.info(f"Navigated to post: {self.driver.current_url}")
    #             return True
    #         else:
    #             self.logger.info("No post links found on the current page")
    #             return False
    #     except Exception as e:
    #         self.logger.error(f"Error navigating to post: {e}")
    #         return False

    # def interact_with_ads_on_post(self):
    #     # Check if the current URL is a post page
    #     if '/post/' not in self.driver.current_url:
    #         self.logger.info("Not on a post page. Skipping ad interaction.")
    #         return 0

    #     ads_clicked = 0
    #     max_attempts = 5  # Limit attempts per post

    #     for _ in range(max_attempts):
    #         if self.click_ad_content():
    #             ads_clicked += 1
    #             self.logger.info(f"Clicked ad {ads_clicked} on post page")
                
    #             # Handle new tab if opened
    #             if len(self.driver.window_handles) > 1:
    #                 self.driver.switch_to.window(self.driver.window_handles[-1])
    #                 self.random_scroll()
    #                 time.sleep(random.uniform(2, 5))
    #                 self.driver.close()
    #                 self.driver.switch_to.window(self.driver.window_handles[0])
    #             else:
    #                 # If the ad opened in the same tab, go back to the post page
    #                 self.driver.back()
                
    #             self.wait_for_page_load()
                
    #             if ads_clicked >= 3:  # Limit to 3 ads per post
    #                 break
    #         else:
    #             self.logger.info("No more clickable ads found on this post")
    #             break

    #     return ads_clicked


    def navigate_to_random_page(self):
        try:
            post_selectors = [
                (By.CSS_SELECTOR, "a[href*='/post/']"),
                (By.CSS_SELECTOR, "a[href*='/category/']")
            ]
            
            all_post_links = []
            
            for selector in post_selectors:
                post_links = self.driver.find_elements(*selector)
                all_post_links.extend([link for link in post_links if link.get_attribute('href').startswith(self.main_url)])
            
            if all_post_links:
                random_link = random.choice(all_post_links)
                self.safe_click(random_link)
                self.wait_for_page_load()
                self.logger.info(f"Navigated to post: {self.driver.current_url}")
                return True
            else:
                self.logger.info("No post links found on the current page")
                return False
        except Exception as e:
            self.logger.error(f"Error navigating to random page: {e}")
            return False



    def detect_and_handle_captcha(self):
        captcha_selectors = [
            (By.ID, "recaptcha"),
            (By.CSS_SELECTOR, ".g-recaptcha"),
            (By.XPATH, "//iframe[contains(@src, 'recaptcha')]"),
            (By.ID, "captcha"),
            (By.CSS_SELECTOR, "img[alt*='CAPTCHA']")
        ]
        
        for selector in captcha_selectors:
            try:
                captcha_element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(selector))
                if captcha_element.is_displayed():
                    self.logger.warning(f"CAPTCHA detected. Attempting to bypass...")
                    # Implement CAPTCHA solving logic here (e.g., using a CAPTCHA solving service)
                    # For now, we'll just log the occurrence and return
                    return True
            except TimeoutException:
                pass
        
        return False
    
    def reconnect_if_necessary(self):
        if not self.is_session_valid():
            self.logger.warning("Browser session became invalid. Attempting to reconnect...")
            try:
                self.driver.quit()
            except:
                pass
            self.driver = self.initialize_driver(max_retries=3)
            self.wait = WebDriverWait(self.driver, 10)
            if self.navigate_with_retry():
                self.logger.info("Successfully reconnected to the browser.")
            else:
                raise Exception("Failed to reconnect to the browser.")

    def is_session_valid(self):
        try:
            self.driver.title
            return True
        except WebDriverException:
            return False


    def run(self):
        try:
            if not self.navigate_with_retry():
                return
            
            # if not self.verify_user_agent() or not self.verify_fingerprint():
            #     self.logger.warning("Browser fingerprint verification failed. Reinitializing driver.")
            #     old_fingerprint = self.get_current_fingerprint()
            #     if old_fingerprint:
            #         self.print_fingerprint(old_fingerprint, "Fingerprint Before Reinitialization")

            #     self.driver.quit()
            #     self.driver = self.initialize_driver(max_retries=3)

            #     new_fingerprint = self.get_current_fingerprint()
            #     if new_fingerprint:
            #         self.print_fingerprint(new_fingerprint, "Fingerprint After Reinitialization")

            #     if not self.navigate_with_retry():
            #         return


            self.wait_for_page_load()
            self.logger.info(f"Successfully loaded the page: {self.main_url}")
            
            # Check for #google_vignette in URL
            if "#google_vignette" in self.driver.current_url:
                vignette_handled = self.handle_google_vignette()
                if not vignette_handled:
                    self.logger.warning("Unable to handle Google Vignette. Refreshing the page...")
                    self.driver.refresh()
                    self.wait_for_page_load()
            
            # Ensure highlight script is injected
            if not self.inject_highlight_script():
                self.logger.warning("Failed to inject highlight script at the start of run")

            # Handle consent modal
            self.handle_consent_modal()
            self.handle_privacy_overlay()

            self.simulate_human_behavior()
            self.random_mouse_movement()
            self.take_screenshot("initial")
            
            # attempts = 0
            # Set the start time just before entering the main ad-clicking loop
            self.start_time = time.time()
            last_print_time = self.start_time

            while self.total_ads_clicked < self.max_ads_to_click:
                try:
                    self.reconnect_if_necessary()

                    # Add a timeout for each iteration
                    start_time = time.time()
                    while time.time() - start_time < 60:  # 60 seconds timeout
                        # Search for and click ads more aggressively
                        ads_clicked = self.search_and_click_ads()
                        if ads_clicked == 0:
                            # If no ads were clicked, navigate to a new page
                            if not self.navigate_to_random_page():
                                self.navigate_with_retry(self.main_url)
                        
                        # Print progress every 5 seconds
                        current_time = time.time()
                        if current_time - last_print_time >= 5:
                            self.print_progress()
                            last_print_time = current_time

                        # Check if we've exceeded the timeout
                        if current_time - self.start_time > self.ad_click_timeout:
                            self.logger.warning("Ad click timeout reached. Ending the session.")
                            break

                        # Check if we're stuck
                        if self.is_page_stuck():
                            self.handle_stuck_situation()
                            break
                        
                        time.sleep(1)  # Short sleep to prevent tight looping

                    # Perform some random actions
                    # self.simulate_human_behavior()
                    
                    # Handle other popups and overlays
                    self.detect_and_handle_popups()
                    
                    # self.take_screenshot(f"action_{attempts}")
                    # time.sleep(random.uniform(2, 5))
                    
                    # attempts += 1
                except Exception as e:
                    self.logger.error(f"An error occurred during bot execution: {e}")
                    if "Browsing context has been discarded" in str(e):
                        self.reconnect_browser()
                    
                    self.handle_stuck_situation()
                    continue

            self.print_progress()  # Print final progress
            print("\n")  # Move to next line after progress bar
            self.logger.info(f"Final total ads clicked: {self.total_ads_clicked}")
            self.take_screenshot("final")
        except Exception as e:
            self.logger.error(f"An error occurred during bot execution: {e}")

        finally:
            if self.driver:
                self.driver.quit()
            self.disconnect_vpn()



    # def run_parallel(self, num_workers=3):
    #     try:
    #         with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
    #             futures = [executor.submit(self.run) for _ in range(num_workers)]
    #             concurrent.futures.wait(futures)
                
    #             for future in futures:
    #                 try:
    #                     future.result()  # This will raise any exceptions that occurred in the threads
    #                 except Exception as e:
    #                     self.logger.error(f"An error occurred in one of the parallel executions: {e}")
    #     except Exception as e:
    #         self.logger.error(f"An error occurred while running in parallel: {e}")
    #     finally:
    #         if self.driver:
    #             self.driver.quit()
    #         self.disconnect_vpn()

if __name__ == "__main__":
    load_dotenv()  # Ensure environment variables are loaded
    url = os.getenv('MAIN_URL')
    print(f"Main URL from environment: {url}")  # Debug print

    max_retries = 3
    for attempt in range(max_retries):
        try:
            bot = BlogBot(url, use_vpn=True, vpn_location="US")
            # bot = BlogBot(url, use_vpn=False)
            bot.run()
            # bot.run_parallel()
            break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print("Retrying in 30 seconds...")
                time.sleep(30)
            else:
                print("Failed to run the bot after multiple attempts")