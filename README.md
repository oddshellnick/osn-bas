# osn-bas: Browser Automation Simplification Library

`osn-bas` is a Python library designed to simplify browser automation tasks using Selenium WebDriver. It provides a set of tools for easy browser management, configuration, and interaction, supporting Chrome, Edge, Firefox, and Yandex browsers on Windows.

## Key Features

`osn-bas` focuses on making browser automation more straightforward and manageable. Its key features include:

*   **Installed Browser Detection:** Automatically detects installed browsers (Chrome, Edge, Firefox, Yandex) on Windows systems, retrieving their names, versions, and paths.
*   **WebDriver Lifecycle Management:**  Manages the entire lifecycle of browser instances, including starting, stopping, and restarting browsers with custom configurations.
*   **Browser Configuration:**  Offers extensive options for browser configuration:
    *   Setting debugging ports for browser control.
    *   Managing browser profiles (user data directories).
    *   Running browsers in headless mode.
    *   Muting audio output in browsers.
    *   Configuring proxy servers.
    *   Setting custom User-Agent strings.
*   **Simplified WebDriver Interface:**  Provides a user-friendly, simplified interface (`BrowserWebDriver`) built upon Selenium, making common WebDriver actions easier to use.
*   **JavaScript Execution:**  Enables execution of JavaScript code within the browser context for advanced interactions and manipulations.
*   **Window Management:**  Simplifies window and tab handling with functions to switch, close, and manage browser windows.
*   **Element Interaction:** Offers easy-to-use functions for finding web elements (single and multiple, inner elements), hovering, scrolling, and getting element styles.
*   **Cross-Browser Support:**  Supports multiple browser types (Chrome, Edge, Firefox, Yandex) with browser-specific implementations and configurations.
*   **Remote WebDriver Connection:**  Allows connection to existing remote WebDriver sessions for controlling browsers running on remote servers.


## Installation

* **With pip:**
    ```bash
    pip install osn-bas
    ```

* **With git:**
    ```bash
    pip install git+https://github.com/oddshellnick/osn-bas.git
    ```

## Usage

Here are some examples of how to use `osn-bas`:

### Getting a list of installed browsers

```python
from osn_bas.browsers_handler import get_installed_browsers

browsers = get_installed_browsers()
for browser in browsers:
    print(f"Name: {browser['name']}, Version: {browser['version']}, Path: {browser['path']}")
```

### Creating and starting a Chrome WebDriver instance

```python
from osn_bas.webdrivers.Chrome import ChromeWebDriver

# Assuming chromedriver is in PATH or webdriver_path is provided
driver = ChromeWebDriver(webdriver_path="path/to/chromedriver") # Provide path if not in PATH
driver.start_webdriver(debugging_port=9222, headless_mode=True)

driver.search_url("https://www.example.com")
print(driver.current_url)

driver.close_webdriver()
```

### Setting browser options and restarting

```python
from osn_bas.webdrivers.Chrome import ChromeWebDriver
from osn_bas.utilities import WindowRect

driver = ChromeWebDriver(webdriver_path="path/to/chromedriver")
driver.start_webdriver(profile_dir="user_profile_dir", proxy="127.0.0.1:8080")

# ... perform actions ...

driver.restart_webdriver(headless_mode=False, window_rect=WindowRect(x=0, y=0, width=1000, height=800))

# ... continue with new settings ...

driver.close_webdriver()
```

### Finding and interacting with web elements

```python
from osn_bas.webdrivers.Chrome import ChromeWebDriver
from selenium.webdriver.common.by import By

driver = ChromeWebDriver(webdriver_path="path/to/chromedriver")
driver.start_webdriver()
driver.search_url("https://www.google.com")

search_box = driver.find_web_element(By.NAME, "q")
search_box.send_keys("Selenium WebDriver")

search_button = driver.find_web_element(By.NAME, "btnK")
search_button.click()

print(driver.current_url)
driver.close_webdriver()
```

### Executing JavaScript and getting element style

```python
from osn_bas.webdrivers.Chrome import ChromeWebDriver
from selenium.webdriver.common.by import By

driver = ChromeWebDriver(webdriver_path="path/to/chromedriver")
driver.start_webdriver()
driver.search_url("https://www.example.com")

element = driver.find_web_element(By.TAG_NAME, "h1")
style = driver.get_element_css_style(element)
print(style.get('font-size')) # Example: get font-size

driver.execute_js_script("alert('Hello from JavaScript!');")

driver.close_webdriver()
```


## Classes and Functions

### Browser Management (`osn_bas.__init__.py`)

*   `get_installed_browsers()`: Retrieves a list of installed browsers on the system.
*   `get_version_of_browser(...)`: Retrieves the version of a specific installed browser by name.
*   `get_path_to_browser(...)`: Retrieves the installation path of a specific installed browser by name.

### Windows Browser Handling (`osn_bas.browsers_handler.windows.py`)

*   `get_installed_browsers_win32()`: Retrieves installed browsers on Windows using registry queries.
*   `get_browser_version(...)`: Gets the version of a browser executable from its file path.
*   `get_webdriver_version(...)`: Retrieves the version of a webdriver executable.

### WebDriver Base Classes (`osn_bas.webdrivers.BaseDriver.py`)

*   `BrowserOptionsManager`: Base class for managing browser options (arguments and experimental options).
*   `BrowserStartArgs`: Base class for managing browser start-up command-line arguments.
*   `EmptyWebDriver`:  A simplified base WebDriver class providing common WebDriver actions.
*   `BrowserWebDriver`: Extends `EmptyWebDriver` to manage the browser instance lifecycle (start, stop, restart), and settings.

### Browser-Specific WebDriver Classes (`osn_bas.webdrivers.Chrome.py`, `osn_bas.webdrivers.Edge.py`, `osn_bas.webdrivers.FireFox.py`, `osn_bas.webdrivers.Yandex.py`)

*   `ChromeWebDriver`, `EdgeWebDriver`, `FirefoxWebDriver`, `YandexWebDriver`: Classes for controlling specific browser types, extending `BrowserWebDriver` with browser-specific options and start arguments managers (`ChromeOptionsManager`, `EdgeOptionsManager`, `FirefoxOptionsManager`, `YandexOptionsManager`, `ChromeStartArgs`, `EdgeStartArgs`, `FirefoxStartArgs`, `YandexStartArgs`). Each class provides `create_driver()` and `remote_connect_driver()` methods.

### Utility Functions (`osn_bas.webdrivers.functions.py`)

*   `read_js_scripts()`: Reads JavaScript scripts from files within the `js_scripts` directory.
*   `find_browser_previous_session(...)`: Finds the debugging port of a previous browser session based on profile directory.
*   `build_first_start_argument(...)`: Builds the initial command line argument to start a browser executable.

### Utility Classes (`osn_bas.utilities.py`)

*   `WindowRect`: Represents a window rectangle with properties for x, y, width, and height, used for setting window position and size.

### Types (`osn_bas.webdrivers.types.py`, `osn_bas.browsers_handler.types.py`)

*   `WebdriverOption`: `TypedDict` for defining webdriver option configurations (name, command, type).
*   `JS_Scripts`: `TypedDict` for storing JavaScript scripts as a collection.
*   `Browser`: `TypedDict` for representing an installed browser with name, path, and version.


## Future Notes

`osn-bas` is under active development. Future enhancements may include:

*   Expanding platform support beyond Windows.
*   Adding more advanced browser automation features and utilities.
*   Improving error handling and logging.
*   Adding support for more browser specific options and configurations.

Contributions and feature requests are welcome to help improve `osn-bas` and make browser automation even easier!


## Note

Please be advised that **Firefox browser support is currently experiencing issues and may not function correctly with `osn-bas`**. Due to these known problems, it is **recommended to avoid using Firefox** with this library for the time being. We are working to resolve these issues in a future update. In the meantime, Chrome, Edge, and Yandex browsers are the recommended and tested browsers for optimal performance with `osn-bas`.