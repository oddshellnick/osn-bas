# osn-bas: Browser Automation Simplification Library

`osn-bas` is a Python library designed to simplify browser automation tasks using Selenium WebDriver. It provides a set of tools for easy browser management, configuration, and interaction, supporting Chrome, Edge, Firefox, and Yandex browsers on Windows. **Now enhanced with powerful DevTools integration for advanced browser control and monitoring.**

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
*   **DevTools Integration**: Leverages the Chrome DevTools Protocol (CDP) through Selenium BiDi for advanced browser control and monitoring. This robust integration offers:
    *   **Asynchronous Event Handling**: Built with `trio`, ensuring non-blocking asynchronous operations when interacting with DevTools, keeping your automation scripts efficient and responsive.
    *   **Network Request Interception and Modification**:  Dynamically intercept and modify network requests, including headers and post data. Utilize handlers for events like `fetch.requestPaused` to customize browser behavior on-the-fly.
    *   **Context Manager for DevTools**:  Effortlessly manage DevTools sessions using an `async with driver.dev_tools as driver_wrapper:` context. This context manager handles the lifecycle of DevTools listeners and connections, ensuring clean and resource-efficient automation.
    *   **Flexible Event Handling Framework**: Set up custom handlers for a wide range of DevTools events. Observe, modify, and react to browser events in real-time, enabling sophisticated automation scenarios.

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
driver = ChromeWebDriver(webdriver_path="path/to/chromedriver", enable_devtools=True)
driver.start_webdriver(debugging_port=9222, headless_mode=True)

driver.search_url("https://www.example.com")
print(driver.current_url)

driver.close_webdriver()
```

### Setting browser options and restarting

```python
from osn_bas.webdrivers.Chrome import ChromeWebDriver
from osn_bas.types import WindowRect
driver = ChromeWebDriver(webdriver_path="path/to/chromedriver", enable_devtools=True)
driver.start_webdriver(profile_dir="user_profile_dir", proxy="127.0.0.1:8080")

# ... perform actions ...

driver.restart_webdriver(headless_mode=False, window_rect=WindowRect(x=0, y=0, width=1000, height=800), enable_devtools=True)

# ... continue with new settings ...

driver.close_webdriver()
```

### Finding and interacting with web elements

```python
from osn_bas.webdrivers.Chrome import ChromeWebDriver
from selenium.webdriver.common.by import By

driver = ChromeWebDriver(webdriver_path="path/to/chromedriver", enable_devtools=True)
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

driver = ChromeWebDriver(webdriver_path="path/to/chromedriver", enable_devtools=True)
driver.start_webdriver()
driver.search_url("https://www.example.com")

element = driver.find_web_element(By.TAG_NAME, "h1")
style = driver.get_element_css_style(element)
print(style.get('font-size'))

driver.execute_js_script("alert('Hello from JavaScript!');")

driver.close_webdriver()
```

### Intercepting and Modifying Network Requests with DevTools

```python
import trio
from osn_bas.webdrivers.Chrome import ChromeWebDriver
from osn_bas.webdrivers.BaseDriver.dev_tools.domains.fetch import HeaderInstance


async def test():
    driver = ChromeWebDriver(webdriver_path="path/to/chromedriver", enable_devtools=True)
    driver.start_webdriver()
    driver.dev_tools.set_request_paused_handler(
        headers_instances={
            "Custom-Header": HeaderInstance(value="modified_by_devtools", instruction="set")
        }
    )
    
    async with driver.dev_tools as driver_wrapper:
        await driver_wrapper.search_url("https://httpbin.org/headers")
        page_source = driver_wrapper.html
        print(page_source)

    driver.close_webdriver()


trio.run(test,)
```


## Classes and Functions

### Browser Management (`osn_bas.browsers_handler`)

*   `__init__.py`:
    *   `get_installed_browsers()`: Retrieves a list of installed browsers on the system.
    *   `get_path_to_browser(browser_name)`: Retrieves the installation path of a specific installed browser by name.
    *   `get_version_of_browser(browser_name)`: Retrieves the version of a specific installed browser by name.
*   `types.py`:
    *   `Browser (TypedDict)`: `TypedDict` for representing an installed browser with name, path, and version.
*   `windows.py`:
    *   `get_installed_browsers_win32()`: Retrieves installed browsers on Windows using registry queries.
    *   `get_browser_version(browser_path)`: Gets the version of a browser executable from its file path.
    *   `get_webdriver_version(driver_path)`: Retrieves the version of a webdriver executable.

### WebDriver Base Classes (`osn_bas.webdrivers.BaseDriver`)

*   `__init__.py`: (Base Driver Initialization)
*   `dev_tools`:
    *   `domains`:
        *   `__init__.py`:
            *   `CallbacksSettings (TypedDict)`: Settings for configuring callbacks for different DevTools event domains.
            *   `Fetch (TypedDict)`: Configuration settings for the Fetch domain of DevTools.
        *   `fetch.py`:
            *   `default_headers_handler(handler_settings, header_entry_class, event)`: Default handler for processing and modifying request headers.
            *   `default_post_data_handler(handler_settings, event)`: Default handler for processing request post data.
            *   `HeaderInstance (TypedDict)`: Type definition for header modification instructions.
            *   `RequestPausedHandlerSettings (TypedDict)`: Settings for handling 'fetch.requestPaused' events.
    *   `errors.py`:
        *   `CantEnterDevToolsContextError(Exception)`: Custom exception raised when unable to enter the DevTools context.
        *   `WrongHandlerSettingsError(Exception)`: Custom exception raised when event handler settings are incorrect.
        *   `WrongHandlerSettingsTypeError(Exception)`: Custom exception raised when the event handler settings type is incorrect.
    *   `manager.py`:
        *   `DevTools`: The core class for handling DevTools functionalities in Selenium WebDriver.
    *   `utils.py`:
        *   `log_on_error(func)`: Decorator to log any exceptions that occur during the execution of the decorated function.
        *   `validate_handler_settings(handler_settings)`: Validates the structure of event handler settings.
        *   `warn_if_active(func)`: Decorator to warn if DevTools operations are attempted while DevTools is active.
    *   `__init__.py`: (DevTools Initialization)
*   `options.py`:
    *   `BrowserOptionsManager`: Base class for managing browser options (arguments and experimental options).
*   `protocols.py`:
    *   `BrowserWebDriverProtocol (Protocol)`: Protocol defining the interface for BrowserWebDriver (synchronous).
    *   `DevToolsProtocol (Protocol)`: Protocol defining the interface for DevTools.
    *   `TrioWebDriverWrapperProtocol (Protocol)`: Protocol defining the asynchronous interface for TrioBrowserWebDriverWrapper.
*   `start_args.py`:
    *   `BrowserStartArgs`: Base class for managing browser start-up command-line arguments.
*   `webdriver.py`:
    *   `BrowserWebDriver`: Extends `EmptyWebDriver` to manage the browser instance lifecycle, settings, and DevTools integration.
    *   `TrioBrowserWebDriverWrapper`: Wraps `BrowserWebDriver` for asynchronous execution in Trio.

### Browser-Specific WebDriver Classes (`osn_bas.webdrivers`)

*   `Chrome.py`:
    *   `ChromeOptionsManager(BrowserOptionsManager)`: Manages Chrome-specific browser options.
    *   `ChromeStartArgs(BrowserStartArgs)`: Manages Chrome-specific browser start arguments.
    *   `ChromeWebDriver(BrowserWebDriver)`: Class for controlling Chrome browser.
*   `Edge.py`:
    *   `EdgeOptionsManager(BrowserOptionsManager)`: Manages Edge-specific browser options.
    *   `EdgeStartArgs(BrowserStartArgs)`: Manages Edge-specific browser start arguments.
    *   `EdgeWebDriver(BrowserWebDriver)`: Class for controlling Edge browser.
*   `FireFox.py`:
    *   `FirefoxOptionsManager(BrowserOptionsManager)`: Manages Firefox-specific browser options.
    *   `FirefoxStartArgs(BrowserStartArgs)`: Manages Firefox-specific browser start arguments.
    *   `FirefoxWebDriver(BrowserWebDriver)`: Class for controlling Firefox browser.
*   `Yandex.py`:
    *   `YandexOptionsManager(BrowserOptionsManager)`: Manages Yandex-specific browser options.
    *   `YandexStartArgs(BrowserStartArgs)`: Manages Yandex-specific browser start arguments.
    *   `YandexWebDriver(BrowserWebDriver)`: Class for controlling Yandex browser.

### Utility Functions (`osn_bas.webdrivers`)

*   `functions.py`:
    *   `build_first_start_argument(browser_exe)`: Builds the initial command line argument to start a browser executable.
    *   `find_browser_previous_session(browser_exe, profile_dir_command, profile_dir)`: Finds the debugging port of a previous browser session based on profile directory.
    *   `get_active_executables_table(browser_exe)`:  (Function description needed)
    *   `get_found_profile_dir(data, profile_dir_command)`: (Function description needed)
    *   `read_js_scripts()`: Reads JavaScript scripts from files within the `js_scripts` directory.
*   `types.py`:
    *   `JS_Scripts (TypedDict)`: `TypedDict` for storing JavaScript scripts as a collection.
    *   `WebdriverOption (TypedDict)`: `TypedDict` for defining webdriver option configurations (name, command, type).

### Root Level Utilities (`osn_bas`)

*   `__init__.py`: (Root Initialization)
*   `errors.py`:
    *   `PlatformNotSupportedError(Exception)`: Custom exception raised when the platform is not supported.
*   `utilities.py`:
    *   `WindowRect`: Represents a window rectangle with properties for x, y, width, and height.

### JavaScript Scripts (`js_scripts`)

*   `get_element_css.js`: JavaScript script to get computed CSS style of an element.
*   `open_new_tab.js`: JavaScript script to open a new tab.
*   `stop_window_loading.js`: JavaScript script to stop window loading.


## Future Notes

`osn-bas` is under active development. Future enhancements may include:

*   Expanding platform support beyond Windows.
*   Adding support for more DevTools domains and functionalities to further enhance browser control and introspection capabilities.
*   Adding more advanced browser automation features and utilities, streamlining complex automation workflows.
*   Improving error handling and logging for more robust and debuggable automation scripts.
*   Adding support for more browser specific options and configurations, providing even finer-grained control over browser behavior.

Contributions and feature requests are welcome to help improve `osn-bas` and make browser automation even easier and more powerful!


## Note

Please be advised that **Firefox browser support is currently experiencing issues and may not function correctly with `osn-bas`**. Due to these known problems, it is **recommended to avoid using Firefox** with this library for the time being. We are working to resolve these issues in a future update. In the meantime, Chrome, Edge, and Yandex browsers are the recommended and tested browsers for optimal performance with `osn-bas`.