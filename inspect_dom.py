import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("http://localhost:8502")
    time.sleep(5) # wait for render

    # Find sidebar collapse button and click it
    collapse_btn = driver.find_elements(By.CSS_SELECTOR, '[data-testid="stSidebarCollapseButton"]')
    if collapse_btn:
        print("Found collapse button, clicking...")
        collapse_btn[0].click()
        time.sleep(2)
    else:
        print("Collapse button not found")

    # Find the expand button (collapsedControl)
    expand_ctrl = driver.find_elements(By.CSS_SELECTOR, '[data-testid="collapsedControl"]')
    if expand_ctrl:
        el = expand_ctrl[0]
        print("Found collapsedControl")
        print("Displayed:", el.is_displayed())
        print("Location:", el.location)
        print("Size:", el.size)
        
        # Check parent hierarchy and CSS
        script = """
        var el = arguments[0];
        var info = [];
        while(el && el.tagName) {
            var style = window.getComputedStyle(el);
            info.push({
                tag: el.tagName,
                id: el.id,
                testId: el.getAttribute('data-testid'),
                display: style.display,
                visibility: style.visibility,
                opacity: style.opacity,
                zIndex: style.zIndex,
                pointerEvents: style.pointerEvents,
                className: el.className
            });
            el = el.parentElement;
        }
        return info;
        """
        hierarchy = driver.execute_script(script, el)
        import json
        print(json.dumps(hierarchy, indent=2))
        
        # Also check what element is at the top left corner (to see if something overlaps)
        overlap_script = """
        var el = document.elementFromPoint(15, 15);
        if(el) {
            return el.tagName + ' ' + el.getAttribute('data-testid') + ' ' + el.className;
        }
        return "None";
        """
        top_el = driver.execute_script(overlap_script)
        print("Element at (15, 15) covering top-left:", top_el)
    else:
        print("collapsedControl not found")

except Exception as e:
    print("Error:", e)
finally:
    driver.quit()
