# osn-bas: A Python Library for Browser Automation

osn-bas simplifies interaction with web browsers for scraping and automation tasks. It currently supports Chrome, Firefox, Edge, and Yandex browsers, providing a consistent interface for managing browser sessions, handling options, and performing common actions.

## Key Features:

*   **Cross-Browser Support:** Seamlessly work with Chrome, Firefox, Edge, and Yandex browsers using a unified API.
*   **Remote WebDriver Control:** Connect to and manage existing browser sessions remotely.
*   **Headless Browsing:** Execute tasks discreetly in the background without a visible browser window.
*   **Proxy Support:** Integrate proxies for managing network requests.
*   **User Agent Spoofing:** Customize the user agent string for various browser impersonations.
*   **Window Management:** Control window size, position, and manage multiple tabs/windows.
*   **Simplified API:** Perform common actions like scrolling, hovering, finding elements, and executing JavaScript.

## Installation:

* **With pip:**
    ```bash
    pip install osn-bas
    ```

* **With git:**
    ```bash
    pip install git+https://github.com/oddshellnick/osn-bas.git
    ```

## API Reference:

*   **BaseDriver:** Provides fundamental classes like `EmptyWebDriver`, `BrowserOptionsManager`, `BrowserStartArgs`, and `BrowserWebDriver` for core browser management functionality.
*   **ChromeDriver/EdgeDriver/FirefoxDriver/YandexDriver:** Contains specific implementations for each browser, including options management, startup argument handling, and remote webdriver connection classes.
*   **browsers_handler:** Includes helper classes like `WindowRect` for managing window dimensions and `get_installed_browsers`/`get_browser_version` for retrieving system browser information.

## Modules Overview:

*   **EmptyWebDriver:** A base class offering essential methods for interacting with a webdriver.
*   **BrowserOptionsManager:** Base class for managing browser-specific options. Subclassed for each browser type.
*   **BrowserStartArgs:** Base class for managing browser startup arguments. Subclassed for each browser.
*   **BrowserWebDriver:** Base class for managing the lifecycle of a webdriver instance. Subclassed for each browser.
*   **Chrome(Remote)WebDriver, Edge(Remote)WebDriver, Firefox(Remote)WebDriver, Yandex(Remote)WebDriver:** Concrete implementations for managing local and remote sessions for each browser.

This library aims to simplify browser automation in Python. Contributions and feedback are welcome!

## Usage Examples:

**Starting a Chrome Webdriver:**

```python
from osn_bas.webdrivers.Chrome import ChromeWebDriver
from osn_bas.utilities import WindowRect

webdriver = ChromeWebDriver(webdriver_path="/path/to/chromedriver", window_rect=WindowRect(0, 0, 800, 600))
webdriver.start_webdriver(headless_mode=True)
webdriver.search_url("https://www.example.com")
# ... perform actions ...
webdriver.close_webdriver()
```

**Connecting to a Remote Chrome Instance:**

```python
from osn_bas.webdrivers.Chrome import ChromeWebDriver
from osn_bas.webdrivers.Chrome import ChromeRemoteWebDriver

webdriver = ChromeWebDriver(webdriver_path="/path/to/chromedriver")
webdriver.start_webdriver()

command_executor, session_id = webdriver.get_vars_for_remote()
remote_webdriver = ChromeRemoteWebDriver(command_executor, session_id)
remote_webdriver.create_driver()
# ...Interact with the remote browser...
remote_webdriver.close_webdriver()
```


## Future Notes

osn-bas is under active development. Planned future enhancements include support for additional browsers, advanced interaction features, and improved handling of dynamic web content. Contributions and suggestions for new features are welcome! Feel free to open issues or submit pull requests on the project's repository.