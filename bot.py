from dotenv import load_dotenv
import os
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, WebDriverException, NoAlertPresentException
import random
import time
import logging
import subprocess
from fake_useragent import UserAgent

class BlogBot:
    def __init__(self, url, use_vpn=False, vpn_location=None, window_size=(1280, 720)):
        self.url = url
        self.ua = UserAgent()
        self.window_size = window_size
        self.driver = None
        self.setup_logging()
        if use_vpn:
            if self.connect_vpn(vpn_location):
                self.wait_for_vpn_connection(timeout=30)
            else:
                raise Exception("Failed to connect to VPN")
        self.setup_driver()

        load_dotenv()

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument(f'--window-size={self.window_size[0]},{self.window_size[1]}')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(f'user-agent={self.ua.random}')
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-infobars')

        try:
            service = Service(r"C:\Program Files\chromedriver-win64\chromedriver.exe")
            self.driver = webdriver.Chrome(service=service, options=options)
            self.disable_webdriver_flags()
            self.logger.info(f"Initialized browser with User-Agent: {self.ua.random}")
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            raise

    def disable_webdriver_flags(self):
        script = """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        """
        self.driver.execute_script(script)

    def wait_for_page_load(self, timeout=30):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            self.logger.info("Page loaded successfully")
        except TimeoutException:
            self.logger.warning(f"Timeout waiting for page load after {timeout} seconds")
        except Exception as e:
            self.logger.error(f"Error waiting for page load: {e}")

    def navigate_with_retry(self, max_retries=3):
        for attempt in range(max_retries):
            try:
                self.driver.get(self.url)
                self.wait_for_page_load()
                self.handle_privacy_overlay()
                if self.url in self.driver.current_url:
                    self.logger.info(f"Successfully navigated to {self.url}")
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
        function highlightClick(x, y) {
            const dot = document.createElement('div');
            dot.style.position = 'absolute';
            dot.style.left = x + 'px';
            dot.style.top = y + 'px';
            dot.style.width = '10px';
            dot.style.height = '10px';
            dot.style.borderRadius = '50%';
            dot.style.backgroundColor = 'red';
            dot.style.zIndex = '10000';
            document.body.appendChild(dot);
            setTimeout(() => dot.remove(), 1000);
        }

        function highlightHover(element) {
            const originalOutline = element.style.outline;
            element.style.outline = '2px solid blue';
            setTimeout(() => element.style.outline = originalOutline, 1000);
        }

        function highlightScroll() {
            const indicator = document.createElement('div');
            indicator.style.position = 'fixed';
            indicator.style.right = '10px';
            indicator.style.top = '10px';
            indicator.style.backgroundColor = 'green';
            indicator.style.color = 'white';
            indicator.style.padding = '5px';
            indicator.style.zIndex = '10000';
            indicator.textContent = 'Scrolling';
            document.body.appendChild(indicator);
            setTimeout(() => indicator.remove(), 1000);
        }
        """
        self.driver.execute_script(highlight_script)

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

        except Exception as e:
            self.logger.error(f"Error handling popups: {e}")

    def simulate_human_behavior(self):
        actions = [
            self.random_scroll,
            self.random_mouse_movement,
            self.click_random_link,
            self.read_article
        ]
        
        for _ in range(random.randint(3, 5)):
            chosen_action = random.choices(actions, weights=[3, 2, 1, 1])[0]
            self.logger.info(f"▶▶▶ PERFORMING ACTION: {chosen_action.__name__.upper()} ◀◀◀")
            try:
                chosen_action()
                self.handle_ad_support_modal()
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
                    if href.startswith(self.url) or random.random() < 0.2:  # 20% chance to click external links
                        # Verify link hover before clicking
                        if self.verify_link_hover(random_link):
                            actions = ActionChains(self.driver)
                            actions.move_to_element(random_link).click().perform()
                            self.logger.info(f"ACTION: Clicked random link - {href}")
                            if not href.startswith(self.url):
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
            (By.CSS_SELECTOR, "div[class*='ad-']"),
            (By.CSS_SELECTOR, "div[id*='ad-']"),
            (By.CSS_SELECTOR, "div[class*='advertisement']"),
            (By.CSS_SELECTOR, "div[id*='advertisement']")
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
                self.logger.info(f"Connected to WindScribe VPN {'server in ' + location if location else 'best server'}")
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

    def wait_for_vpn_connection(self, timeout=30):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                result = subprocess.run(["C:\\Program Files\\Windscribe\\windscribe-cli.exe", "status"], capture_output=True, text=True, check=True)
                if "CONNECTED" in result.stdout:
                    self.logger.info("VPN connection confirmed")
                    return True
            except subprocess.CalledProcessError:
                pass
            time.sleep(2)
        
        self.logger.error(f"VPN connection timeout after {timeout} seconds")
        return False

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

    
    def handle_google_vignette(self):
        try:
            overlay_selectors = [
                "div[id^='google_ads_iframe']",
                "iframe[id^='google_ads_iframe']",
                "div[id^='google_vignette']",
                "div[class*='google-vignette']",
                "div[class*='vignette-container']",
                "div[class*='overlay']",
                "div[class*='modal']",
                "div[style*='position: fixed']"
            ]
            
            for selector in overlay_selectors:
                try:
                    overlay = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    self.logger.info(f"Overlay ad detected using selector: {selector}")
                    
                    # Try to find and click the close button
                    close_button_selectors = [
                        "button[aria-label='Close ad']",
                        ".close-button",
                        "#dismiss-button",
                        "div[aria-label='Close ad']",
                        "div[role='button'][aria-label='Close']",
                        "span[aria-label='Close']",
                        "img[alt='close button']",
                        "span[class*='close']",
                        "div[class*='close']",
                        "[class*='dismiss']",
                        "[id*='dismiss']"
                    ]
                    
                    for close_selector in close_button_selectors:
                        try:
                            close_button = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, close_selector))
                            )
                            self.driver.execute_script("arguments[0].click();", close_button)
                            self.logger.info(f"Clicked close button on overlay ad using selector: {close_selector}")
                            time.sleep(2)
                            return True
                        except:
                            continue
                    
                    # If no close button found, try to click outside the ad
                    actions = ActionChains(self.driver)
                    actions.move_by_offset(-50, -50).click().perform()
                    self.logger.info("Attempted to close overlay ad by clicking outside")
                    time.sleep(2)
                    
                    # If no close button found, try to click the ad
                    clickable = self.find_clickable_element(overlay)
                    if clickable:
                        self.safe_click(clickable)
                        self.logger.info(f"Clicked on ad: {selector}")
                        return True, True  # Indicate that an ad was clicked

                    # Check if the overlay is still present
                    try:
                        overlay = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if not overlay.is_displayed():
                            self.logger.info("Overlay ad closed successfully")
                            return True
                    except:
                        self.logger.info("Overlay ad closed successfully")
                        return True
                    
                    # If still present, try to use JavaScript to remove the overlay
                    self.driver.execute_script("""
                        var elements = document.querySelectorAll('div[style*="position: fixed"], div[class*="overlay"], div[class*="modal"]');
                        for(var i=0; i<elements.length; i++){
                            elements[i].parentNode.removeChild(elements[i]);
                        }
                    """)
                    self.logger.info("Attempted to remove overlay ad using JavaScript")
                    time.sleep(2)
                    
                    # Final check
                    try:
                        overlay = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if not overlay.is_displayed():
                            self.logger.info("Overlay ad removed successfully")
                            return True
                    except:
                        self.logger.info("Overlay ad removed successfully")
                        return True
                    
                except TimeoutException:
                    continue
            
            self.logger.info("No overlay ad detected or unable to close")
            return False, False
        except Exception as e:
            self.logger.error(f"Error handling overlay ad: {e}")
            return False, False

    def reconnect_browser(self):
        self.logger.info(f"Browser connection lost. Attempting to reconnect...")
        try:
            self.driver.quit()
        except:
            pass
        self.setup_driver()
        self.driver.get(self.url)
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

    def click_ad_content(self):
        try:
            ad_selectors = [
                (By.CSS_SELECTOR, "ins.adsbygoogle"),
                (By.CSS_SELECTOR, "iframe[src*='googleadservices']"),
                (By.CSS_SELECTOR, "div[id^='google_ads_iframe']"),
                (By.XPATH, "//iframe[contains(@id, 'google_ads_iframe')]"),
                (By.CSS_SELECTOR, "div[id^='ad-']"),
                (By.CSS_SELECTOR, "div[class*='ad-']"),
                (By.CSS_SELECTOR, "div[class*='advertisement']")
            ]
            
            for selector in ad_selectors:
                ad_elements = self.driver.find_elements(*selector)
                for ad_element in ad_elements:
                    if ad_element.is_displayed():
                        self.logger.info(f"Found visible ad: {selector}")
                        
                        # Scroll to the ad
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", ad_element)
                        time.sleep(random.uniform(1, 2))
                    
                        self.highlight_element(ad_element)
                        self.logger.info(f"Highlighted ad: {selector}")
                        
                        # Simulate hover
                        actions = ActionChains(self.driver)
                        actions.move_to_element(ad_element).perform()
                        time.sleep(random.uniform(0.5, 1))
                        
                        # Click the ad
                        clickable = self.find_clickable_element(ad_element)
                        if clickable:
                            self.safe_click(clickable)
                            self.logger.info(f"Clicked on ad content: {selector}")
                            
                            # Handle new tab if opened
                            self.handle_new_tab()
                        else:
                            self.logger.info("No clickable element found within the ad")
                        return
            
            self.logger.info("No clickable ad content found")
        except Exception as e:
            self.logger.error(f"Error interacting with ad content: {e}")

    def find_clickable_element(self, element):
        try:
            clickable = element.find_element(By.CSS_SELECTOR, "a, button, [role='button'], [tabindex='0']")
            return clickable
        except NoSuchElementException:
            return None

    def handle_new_tab(self):
        try:
            if len(self.driver.window_handles) > 1:
                self.driver.switch_to.window(self.driver.window_handles[-1])
                # Wait for the page to load
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                self.logger.info(f"New tab opened. Title: {self.driver.title}")

                # Perform some actions on the new page (e.g., scroll)
                self.random_scroll()
                time.sleep(random.uniform(3, 5))
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
        except Exception as e:
            self.logger.error(f"Error handling new tab: {e}")

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
            self.setup_driver()
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
            
            self.wait_for_page_load()
            self.logger.info(f"Successfully loaded the page: {self.url}")
            
            self.inject_highlight_script()
            self.simulate_human_behavior()
            self.random_mouse_movement()
            self.take_screenshot("initial")
            
            overlay_handled = False
            for i in range(random.randint(5, 8)):
                try:
                    self.reconnect_if_necessary()
                    
                    if not overlay_handled:
                        overlay_handled, ad_clicked = self.handle_google_vignette()
                        if ad_clicked:
                            # Wait for the ad page to load
                            self.wait_for_page_load()
                            # Perform some actions on the ad page
                            self.random_scroll()
                            time.sleep(random.uniform(3, 5))
                            # Go back to the original page
                            self.driver.back()
                            self.wait_for_page_load()
                            continue

                    self.switch_to_iframe_and_handle_vignette()
                    action = random.choice(['scroll', 'click_post', 'check_ad', 'mouse_move', 'simulate_human'])
                    
                    if action == 'scroll':
                        self.random_scroll()
                        self.handle_ad_support_modal()
                    elif action == 'click_post':
                        if self.click_random_link():
                            time.sleep(random.uniform(2, 5))
                            self.handle_google_vignette()
                            # Check if we're on a different page and switch back to the main page
                            if len(self.driver.window_handles) > 1:
                                self.driver.switch_to.window(self.driver.window_handles[0])
                                print("Switched back to the main page")
                    elif action == 'check_ad':
                        if self.click_ad_content():
                            time.sleep(random.uniform(5, 10))
                            if len(self.driver.window_handles) > 1:
                                self.driver.close()
                                self.driver.switch_to.window(self.driver.window_handles[0])
                                print("Closed ad tab and switched back to the main page")
                    elif action == 'mouse_move':
                        self.random_mouse_movement()
                    else:
                        self.simulate_human_behavior()
                    
                    
                    self.take_screenshot(f"action_{i}")
                    time.sleep(random.uniform(2, 5))
                except Exception as e:
                    self.logger.error(f"An error occurred during bot execution: {e}")
                    if "Browsing context has been discarded" in str(e):
                        self.reconnect_browser()
                    continue

            # Final ad interaction
            self.click_ad_content()
            self.take_screenshot("final")
        except Exception as e:
            self.logger.error(f"An error occurred during bot execution: {e}")

        finally:
            if self.driver:
                self.driver.quit()
            self.disconnect_vpn()

if __name__ == "__main__":
    url = "https://www.progrmrslife.com"
    max_retries = 3
    for attempt in range(max_retries):
        try:
            bot = BlogBot(url, use_vpn=True, vpn_location="US")
            bot.run()
            break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print("Retrying in 30 seconds...")
                time.sleep(30)
            else:
                print("Failed to run the bot after multiple attempts")