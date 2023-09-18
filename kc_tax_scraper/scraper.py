import time
from selenium import webdriver
import pandas as pd
from datetime import datetime

def get_parcel_info(parcel):
    # Website says it throttles at 100 requests / 15min but I have gotten throttled at 81
    # Bringing down to 60 seems to work.
    print(parcel)
    browser = webdriver.Chrome()
    browser.get("https://payment.kingcounty.gov/Home/Index?app=PropertyTaxes")
    time.sleep(7)
    if browser.find_element("xpath", "/html/body").text == "API calls quota exceeded! maximum admitted 1000 per 12h.":
        print(datetime.now())
        print("API calls quota exceeded, waiting for 12 hours...")
        time.sleep(43200)
        browser.get("https://payment.kingcounty.gov/Home/Index?app=PropertyTaxes")
    browser.find_element("id", 'searchParcel').send_keys(parcel)
    time.sleep(3)
    browser.find_element("xpath", '//*[@id="ec-tenant-app"]/div/div/div[2]/div[1]/div[1]/form/div/span/button').click()
    time.sleep(5)
    tax_info_string = browser.find_element("xpath", '/html/body/div[1]/div/div/div/div[3]/div/div[2]/div/div/div/div/div[2]/div[1]/div[3]/div/div/div/div[1]/h4/a/span/span').text
    tax_account_number = tax_info_string[20:]
    print(tax_account_number)
    status = browser.find_element("id", 'payment-details-panel' + str(tax_account_number)).text
    print(status)
    payer_address = browser.find_element("xpath", '//*[@id="collapse' + str(tax_account_number) + '"]/div/div[1]/div[2]/p[2]').text
    print(payer_address)
    browser.close()
    browser.quit()
    return tax_account_number, status, payer_address


parcel_data = pd.read_csv('kc_tax_scraper/98117.csv')
parcel_list = parcel_data["Parcel number"].tolist()
parcel_data["Tax account number"] = ""
parcel_data["Payer address"] = ""
parcel_data["Status"] = ""
for index, row in parcel_data.iterrows():
    print(index)
    tax_account_number, status, payer_address = "", "", ""
    try:
        tax_account_number, status, payer_address = get_parcel_info(row["Parcel number"])
    except KeyboardInterrupt:
        parcel_data.to_csv('kc_tax_scraper/out.csv')
        exit()
    except:
        print("Error pulling parcel: " + str(row["Parcel number"]))
    parcel_data.loc[index, 'Tax account number'] = tax_account_number
    parcel_data.loc[index, 'Payer address'] = payer_address
    parcel_data.loc[index, 'Status'] = status


parcel_data.to_csv('kc_tax_scraper/out.csv')
