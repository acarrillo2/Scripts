import time
from selenium import webdriver

# Create a chrome browser instance
browser = webdriver.Chrome()

# Go to a web page
browser.get("https://github.com/acarrillo2/Scripts/blob/mainline/selenium_example/simple_example.py")
time.sleep(5)

# Click the download button
elem = browser.find_element("xpath", '//*[@id="repos-sticky-header"]/div[1]/div[2]/div[2]/div[1]/div[1]/span')
elem.click()
time.sleep(10)

# Close/Quit so you don't have a bunch of pages open
browser.close()
browser.quit()