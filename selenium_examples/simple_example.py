import time
from selenium import webdriver

# Create a chrome browser instance
browser = webdriver.Chrome()

# Go to a web page
browser.get("https://github.com/acarrillo2")

# Wait for a few seconds
time.sleep(5)

# Close/Quit so you don't have a bunch of pages open
browser.close()
browser.quit()