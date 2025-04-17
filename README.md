# osn-bas: Browser Automation Simplification Library

`osn-bas` is a Python library designed to simplify browser automation tasks using Selenium WebDriver. It provides a set of tools for easy browser management, configuration, and interaction, supporting Chrome, Edge, Firefox, and Yandex browsers on Windows. **Now enhanced with powerful DevTools integration for advanced browser control and monitoring.**

## Key Features

`osn-bas` focuses on making browser automation more straightforward and manageable. Its key features include:

*   **Installed Browser Detection:** Automatically detects installed browsers (Chrome, Edge, Firefox, Yandex) on Windows systems, retrieving their names, versions, and paths.
*   **WebDriver Lifecycle Management:** Manages the entire lifecycle of browser instances, including starting (`start_webdriver`), stopping (`close_webdriver`), and restarting (`restart_webdriver`) browsers with custom configurations.
*   **Flexible Browser Configuration:** Offers extensive options for browser configuration via dedicated `OptionsManager` and `StartArgs` classes for each browser:
    *   Setting debugging ports for remote control or session reuse.
    *   Managing browser profiles (user data directories).
    *   Running browsers in headless mode.
    *   Muting audio output.
    *   Configuring proxy servers (single or random choice from a list).
    *   Setting custom User-Agent strings.
    *   Hiding automation flags (`hide_automation`).
    *   Setting the initial window size and position (`WindowRect`).
    *   Defining the start page URL.
*   **Simplified WebDriver Interface:** Provides a unified `BrowserWebDriver` interface built upon Selenium, abstracting browser-specific details and simplifying common actions.
*   **JavaScript Execution:** Enables execution of predefined (`read_js_scripts`) and custom JavaScript code (`execute_js_script`) within the browser context for advanced interactions (e.g., checking viewport visibility, getting element styles, retrieving viewport info).
*   **Window & Tab Management:** Simplifies window/tab handling with functions to get handles (`windows_handles`, `current_window_handle`, `get_window_handle`), switch focus (`switch_to_window`, `switch_to_frame`), open new tabs (`open_new_tab`), and close windows (`close_window`, `close_all_windows`).
*   **Enhanced Element Interaction:** Offers robust functions for:
    *   Finding elements (`find_web_element`, `find_web_elements`).
    *   Finding elements within other elements (`find_inner_web_element`, `find_inner_web_elements`).
    *   Getting element styles (`get_element_css_style`) and viewport relative rectangles (`get_element_rect_in_viewport`).
    *   Checking if an element is in the viewport (`check_element_in_viewport`).
    *   Generating random points within an element's visible area (`get_random_element_point_in_viewport`).
    *   Building and performing complex interactions using `ActionChains` (`build_action_chains`, `click_action`, `drag_and_drop_action`, `scroll_to_element_action`, `send_keys_action`, etc.).
    *   **Simulating Human-Like Interactions:** Provides methods (`build_hm_move_action`, `build_hm_scroll_action`, `build_hm_text_input_action`, etc.) to create more natural mouse movements, scrolling, and typing sequences by breaking actions into smaller steps with pauses.
* **Cross-Browser Support:** Supports multiple browser types (Chrome, Edge, Firefox, Yandex) with specific implementations (`ChromeWebDriver`, `EdgeWebDriver`, `FirefoxWebDriver`, `YandexWebDriver`).
*   **Remote WebDriver Connection:** Allows connection to existing remote WebDriver sessions (`remote_connect_driver`) using the command executor and session ID (`get_vars_for_remote`).
*   **Asynchronous Operations with Trio:** Includes `TrioBrowserWebDriverWrapper` to seamlessly integrate synchronous WebDriver operations into asynchronous `trio` applications using `trio.to_thread.run_sync`.
*   **Powerful DevTools Integration (via Selenium BiDi & CDP):**
    *   **Asynchronous Context Manager:** Manage DevTools sessions easily with `async with driver.dev_tools as driver_wrapper: ...`. This handles BiDi connection setup, listener management, and cleanup.
    *   **Network Request Interception & Modification:** Intercept network requests using the Fetch domain (`fetch.requestPaused`). Modify headers (`HeaderInstance`) and post data using default or custom handlers (`set_request_paused_handler`, `default_headers_handler`, `default_post_data_handler`).
    *   **Event Handling Framework:** Built on `trio` for non-blocking, asynchronous handling of various DevTools events. (Currently focused on Fetch domain).
    *   **Structured Settings:** Uses `TypedDict`s (`CallbacksSettings`, `Fetch`, `RequestPausedHandlerSettings`) for clear configuration of DevTools event handling.
    *   **Error Handling & Utilities:** Includes specific error types (`CantEnterDevToolsContextError`, etc.) and utility decorators (`@warn_if_active`, `@log_on_error`) for robust DevTools interaction.

## Installation

*   **With pip:**
    ```bash
    pip install osn-bas
    ```

*   **With git:**
    ```bash
    pip install git+https://github.com/oddshellnick/osn-bas.git
    ```
    *(Ensure you have git installed)*

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

# Assuming chromedriver is in PATH or webdriver_path points to it
# enable_devtools=True is required for DevTools features
driver = ChromeWebDriver(webdriver_path="path/to/chromedriver", enable_devtools=True)
# Start with specific options
driver.start_webdriver(debugging_port=9222, headless_mode=True, start_page_url="about:blank")

driver.search_url("https://www.example.com")
print(driver.current_url)

driver.close_webdriver()
```

### Setting browser options and restarting

```python
from osn_bas.webdrivers.Chrome import ChromeWebDriver
from osn_bas.types import WindowRect

# enable_devtools=True is required if you plan to use DevTools later
driver = ChromeWebDriver(webdriver_path="path/to/chromedriver", enable_devtools=True)
driver.start_webdriver(profile_dir="path/to/user_profile_dir", proxy="127.0.0.1:8080")

# ... perform actions ...
print(f"Initial URL: {driver.current_url}")

# Restart with different settings (DevTools remains enabled implicitly)
driver.restart_webdriver(headless_mode=False, window_rect=WindowRect(x=0, y=0, width=1000, height=800))

# ... continue with new settings ...
driver.search_url("https://www.google.com")
print(f"URL after restart: {driver.current_url}")

driver.close_webdriver()
```

### Finding and interacting with web elements

```python
from osn_bas.webdrivers.Chrome import ChromeWebDriver
from selenium.webdriver.common.by import By

# enable_devtools can be False if DevTools are not needed for this task
driver = ChromeWebDriver(webdriver_path="path/to/chromedriver", enable_devtools=False)
driver.start_webdriver()
driver.search_url("https://www.google.com")

# Find the search box by name
search_box = driver.find_web_element(By.NAME, "q")
# Use ActionChains via the driver method for clarity
driver.send_keys_to_element_action(search_box, "Selenium WebDriver").perform()

# Find the search button (might need adjustment based on Google's current layout)
# Using a more robust selector like XPath might be better
search_button = driver.find_web_element(By.XPATH, "(//input[@name='btnK'])[2]") # Example XPath
driver.click_action(search_button).perform()

print(f"Search results URL: {driver.current_url}")
driver.close_webdriver()
```

### Executing JavaScript and getting element style

```python
from osn_bas.webdrivers.Chrome import ChromeWebDriver
from selenium.webdriver.common.by import By

# enable_devtools=False is sufficient here
driver = ChromeWebDriver(webdriver_path="path/to/chromedriver", enable_devtools=False)
driver.start_webdriver()
driver.search_url("https://www.example.com")

element = driver.find_web_element(By.TAG_NAME, "h1")
style = driver.get_element_css_style(element)
print(f"H1 Font Size: {style.get('font-size')}")

# Execute custom JS
driver.execute_js_script("alert('Hello from osn-bas JavaScript!');")
# Note: Handling the alert might require additional steps depending on the driver/browser

driver.close_webdriver()
```

### Intercepting and Modifying Network Requests with DevTools (Async Example)

```python
import trio
from osn_bas.webdrivers.Chrome import ChromeWebDriver
# Import necessary types for DevTools configuration
from osn_bas.webdrivers.BaseDriver.dev_tools.domains.fetch import HeaderInstance

async def test_devtools_interception():
    # enable_devtools=True is MANDATORY for DevTools
    driver = ChromeWebDriver(webdriver_path="path/to/chromedriver", enable_devtools=True)
    # Start the driver *before* setting DevTools handlers
    driver.start_webdriver()

    # Configure the request handler before entering the async context
    driver.dev_tools.set_request_paused_handler(
        headers_instances={
            # Add/Set a custom header for all requests
            "X-Modified-By": HeaderInstance(value="osn-bas-DevTools", instruction="set"),
            # Remove the User-Agent header
            "User-Agent": HeaderInstance(value="", instruction="remove")
        }
        # You can also provide custom post_data_handler and headers_handler functions
    )

    print("Entering DevTools context...")
    # Use the async context manager for DevTools
    async with driver.dev_tools as driver_wrapper:
        print("Navigating with DevTools active...")
        # Use the wrapped driver for async operations inside the context
        await driver_wrapper.search_url("https://httpbin.org/headers") # httpbin reflects request headers

        # Get page source to see the result
        page_source = driver_wrapper.html
        print("\nPage Source (showing modified headers):")
        print(page_source) # Look for "X-Modified-By" and the absence of "User-Agent"

        # Perform other async actions if needed
        await trio.sleep(1)

    print("Exited DevTools context. Listeners stopped.")

    # Close the driver outside the async context
    driver.close_webdriver()
    print("WebDriver closed.")

# Run the async function using trio
trio.run(test_devtools_interception,)
```

## Classes and Functions

### Browser Management (`osn_bas.browsers_handler`)

*   `__init__.py`:
    *   `get_installed_browsers()`: Retrieves a list (`list[Browser]`) of installed browsers on Windows.
    *   `get_path_to_browser(browser_name)`: Retrieves the installation path (`pathlib.Path`) for a specific browser.
    *   `get_version_of_browser(browser_name)`: Retrieves the version string for a specific browser.
*   `types.py`:
    *   `Browser (TypedDict)`: Represents an installed browser (`name`, `path`, `version`).
*   `windows.py`: (Internal Windows-specific implementation)
    *   `get_installed_browsers_win32()`: Windows registry lookup.
    *   `get_browser_version(browser_path)`: Gets version from file properties.
    *   `get_webdriver_version(driver_path)`: Gets version from webdriver `--version` output.

### Core Types (`osn_bas.types`)

*   `WindowRect`: Class representing a window rectangle (`x`, `y`, `width`, `height`) with defaults based on screen size.
*   `Size (TypedDict)`: Represents width and height.
*   `Rectangle (TypedDict)`: Represents x, y, width, height.
*   `Position (TypedDict)`: Represents x, y coordinates.

### Root Errors (`osn_bas.errors`)

*   `PlatformNotSupportedError(Exception)`: Raised for unsupported operating systems.

### WebDriver Base Classes (`osn_bas.webdrivers.BaseDriver`)

*   `options.py`:
    *   `BrowserOptionsManager`: Abstract base class for managing browser options (`add_argument`, `add_experimental_option`, etc.). Provides common methods like `set_debugger_address`, `set_proxy`, `set_user_agent`, `set_enable_bidi`. Requires `renew_webdriver_options` and `hide_automation` implementation in subclasses.
*   `start_args.py`:
    *   `BrowserStartArgs`: Base class managing command-line arguments (`debugging_port`, `profile_dir`, `headless_mode`, etc.). Constructs the final `start_command`.
*   `webdriver.py`:
    *   `BrowserWebDriver`: The core synchronous WebDriver class.
        *   Manages browser options (`_webdriver_options_manager`) and start arguments (`_webdriver_start_args`).
        *   Handles WebDriver lifecycle (`start_webdriver`, `close_webdriver`, `restart_webdriver`, `check_webdriver_active`).
        *   Provides simplified methods for common Selenium actions (finding elements, navigation, actions, window management).
        *   Integrates JavaScript execution (`execute_js_script`, uses scripts from `js_scripts` folder).
        *   Manages timeouts (`set_driver_timeouts`, `update_times`).
        *   Includes builders for human-like action sequences (`build_hm_move_action`, `build_hm_scroll_action`, `build_hm_text_input_action`, etc.).
        *   Handles remote connections (`get_vars_for_remote`, `remote_connect_driver` - implemented in subclasses).
        *   Initializes and holds the `DevTools` instance (`dev_tools`).
        *   Provides `to_wrapper()` to get the async wrapper.
    *   `TrioBrowserWebDriverWrapper`: Asynchronous wrapper using `trio.to_thread.run_sync` for non-blocking WebDriver calls in `trio` applications. Mirrors `BrowserWebDriver`'s interface asynchronously.
*   `protocols.py`:
    *   `BrowserWebDriverProtocol (Protocol)`: Defines the expected synchronous interface of `BrowserWebDriver`.
    *   `DevToolsProtocol (Protocol)`: Defines the expected interface of the `DevTools` manager.
    *   `TrioWebDriverWrapperProtocol (Protocol)`: Defines the expected asynchronous interface of `TrioBrowserWebDriverWrapper`.

### DevTools Integration (`osn_bas.webdrivers.BaseDriver.dev_tools`)

*   `manager.py`:
    *   `DevTools`: Manages the BiDi connection, CDP sessions, and event listeners.
        *   Handles the async context (`__aenter__`, `__aexit__`) using `trio`.
        *   Starts/stops listeners (`_start_listeners`, `_run_event_listener`).
        *   Manages target discovery and session handling (`_process_new_targets`, `_handle_new_target`).
        *   Provides methods to configure handlers (`set_request_paused_handler`, `remove_request_paused_handler_settings`).
*   `domains`:
    *   `__init__.py`: Defines `CallbacksSettings (TypedDict)` and `Fetch (TypedDict)` for structuring DevTools settings.
    *   `fetch.py`: Contains specifics for the Fetch domain.
        *   `HeaderInstance (TypedDict)`: Defines how to modify a specific header.
        *   `RequestPausedHandlerSettings (TypedDict)`: Structure for configuring `fetch.requestPaused` handling.
        *   `default_post_data_handler(...)`: Default logic for handling post data.
        *   `default_headers_handler(...)`: Default logic for modifying headers based on `HeaderInstance` instructions.
*   `errors.py`:
    *   `CantEnterDevToolsContextError(Exception)`: Failed to enter DevTools context.
    *   `WrongHandlerSettingsError(Exception)`: Handler settings structure is wrong.
    *   `WrongHandlerSettingsTypeError(Exception)`: Handler settings type is not dict.
*   `_utils.py`:
    *   `@warn_if_active`: Decorator to prevent modifying settings while DevTools context is active.
    *   `validate_handler_settings`: Checks if handler settings dictionary is valid.
    *   `@log_on_error`: Decorator to log exceptions occurring in async tasks.

### Browser-Specific WebDriver Classes (`osn_bas.webdrivers`)

*   Each module (`Chrome.py`, `Edge.py`, `FireFox.py`, `Yandex.py`) contains:
    *   `[Browser]OptionsManager(BrowserOptionsManager)`: Implements browser-specific option handling (e.g., Chrome uses `webdriver.ChromeOptions`). Implements `hide_automation`.
    *   `[Browser]StartArgs(BrowserStartArgs)`: Defines browser-specific command-line argument formats.
    *   `[Browser]WebDriver(BrowserWebDriver)`: The main class for the specific browser. Initializes with the correct managers/args. Implements `create_driver` and `remote_connect_driver` using the appropriate Selenium driver (`webdriver.Chrome`, `webdriver.Edge`, etc.).

### WebDriver Utilities (`osn_bas.webdrivers`)

*   `_functions.py`:
    *   `read_js_scripts()`: Reads JS files from `js_scripts` directory into a `JS_Scripts` TypedDict.
    *   `find_browser_previous_session(...)`: Finds debugging port of a running session matching a profile (Windows-specific).
    *   `get_active_executables_table(...)`: Gets browser processes listening on localhost (Windows-specific `netstat`).
    *   `get_found_profile_dir(...)`: Extracts profile dir from process command line (Windows-specific `wmic`).
    *   `build_first_start_argument(...)`: Formats the browser executable path for command line.
*   `types.py`:
    *   `WebdriverOption (TypedDict)`: Defines structure for options (`name`, `command`, `type`).
    *   `JS_Scripts (TypedDict)`: Maps script names (like `check_element_in_viewport`) to their JS code content.

### JavaScript Scripts (`osn_bas/webdrivers/BaseDriver/js_scripts`)

*   `check_element_in_viewport.js`: Checks if an element is visible within the viewport.
*   `get_document_scroll_size.js`: Gets the full scrollable width/height of the document.
*   `get_element_css.js`: Retrieves all computed CSS styles for an element.
*   `get_element_rect_in_viewport.js`: Gets an element's position and size relative to the viewport.
*   `get_random_element_point_in_viewport.js`: Finds a random clickable point within the visible part of an element.
*   `get_viewport_position.js`: Gets the viewport's current scroll offsets (X, Y).
*   `get_viewport_rect.js`: Gets the viewport's scroll offsets and dimensions.
*   `get_viewport_size.js`: Gets the viewport's current width and height.
*   `open_new_tab.js`: Opens a new browser tab/window.
*   `stop_window_loading.js`: Executes `window.stop()`.

## Future Notes

`osn-bas` is under active development. Future enhancements may include:

*   Expanding platform support beyond Windows.
*   Adding support for more DevTools domains and functionalities (e.g., Network, Performance, Log) to further enhance browser control and introspection capabilities.
*   Implementing more advanced browser automation features and utilities, streamlining complex workflows.
*   Improving error handling and logging for more robust and debuggable automation scripts.
*   Adding support for more browser-specific options and configurations.
*   Refining asynchronous operations and integration with other async frameworks.

Contributions and feature requests are welcome to help improve `osn-bas` and make browser automation even easier and more powerful!

## Note

Please be advised that **Firefox browser support is currently experiencing issues and may not function correctly with `osn-bas`**, especially concerning DevTools integration which relies heavily on BiDi protocols often better supported in Chromium-based browsers. Due to these known problems, it is **recommended to avoid using Firefox** with this library for the time being, particularly for DevTools features. We are working to resolve these issues in a future update. In the meantime, Chrome, Edge, and Yandex browsers are the recommended and tested browsers for optimal performance with `osn-bas`.