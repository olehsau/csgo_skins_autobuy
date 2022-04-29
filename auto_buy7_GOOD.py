from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select
import time

driver = webdriver.Chrome()#chrome_options=options

#########################################################
links = ["https://steamcommunity.com/market/listings/730/CZ75-Auto%20%7C%20Distressed%20%28Minimal%20Wear%29",
         "https://steamcommunity.com/market/listings/730/R8%20Revolver%20%7C%20Bone%20Forged%20%28Minimal%20Wear%29",
         "https://steamcommunity.com/market/listings/730/MP5-SD%20%7C%20Desert%20Strike%20%28Minimal%20Wear%29",
         "https://steamcommunity.com/market/listings/730/Negev%20%7C%20Prototype%20%28Minimal%20Wear%29",
         "https://steamcommunity.com/market/listings/730/R8%20Revolver%20%7C%20Bone%20Forged%20%28Factory%20New%29",
         "https://steamcommunity.com/market/listings/730/Negev%20%7C%20Prototype%20%28Factory%20New%29",
         "https://steamcommunity.com/market/listings/730/Dual%20Berettas%20%7C%20Shred%20%28Factory%20New%29",
         "https://steamcommunity.com/market/listings/730/AUG%20%7C%20Amber%20Slipstream%20%28Factory%20New%29",
         "https://steamcommunity.com/market/listings/730/SCAR-20%20%7C%20Outbreak%20%28Factory%20New%29"]

max_prices = [2.90, 2.90, 2.90, 2.90, 6.3, 6.3, 8.0, 8.06, 9]

max_floats = [0.0902, 0.0902, 0.0902, 0.0902, 0.042, 0.042, 0.042, 0.041, 0.042]
#########################################################
assert (len(links)==len(max_prices)) and (len(max_prices)==len(max_floats)), "links, prices and floats can not have different lengths!"

def priceSTR_to_float(price):
    if(price=="Продано!"):
        return "Продано!"
    price = price[0:-1]
    price = price.replace(',','.')
    return float(price)

driver.get("https://steamcommunity.com/login/home/?goto=")
WebDriverWait(driver, 4321).until(expected_conditions.presence_of_element_located((By.ID, "account_pulldown")))
print(">logged in")

# setting page size to 100 
driver.get(links[0])
WebDriverWait(driver, 100).until(expected_conditions.visibility_of_element_located((By.ID, "pageSize")))
Select(driver.find_element_by_id("pageSize")).select_by_value("100")
while(driver.find_element_by_id("searchResults_end").text!="100"): # wait until 100 on page
    time.sleep(0.5)

# main cycle
while(True):
    for l in reversed(range(len(links))):  #for each link
        driver.get(links[l])
        if(len(driver.find_elements_by_class_name("market_listing_table_message"))>0): # check for error
            continue
        #WebDriverWait(driver, 30).until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, "market_listing_price_with_fee")))
        fdsjohfsd = 0
        checker=False
        while(len(driver.find_elements_by_class_name("market_listing_price_with_fee"))==0 or driver.find_element_by_class_name("market_listing_price_with_fee").is_displayed()==False):
            time.sleep(0.3)
            fdsjohfsd = fdsjohfsd+1
            if(fdsjohfsd>=180):
                checker=True
                break
        if(checker==True):
            continue
        while(priceSTR_to_float(driver.find_element_by_class_name("market_listing_price_with_fee").text) <= max_prices[l]):  #for each tab
            if(len(driver.find_elements_by_class_name("market_listing_table_message"))>=1 and driver.find_element_by_class_name("market_listing_table_message").is_displayed()): #if there is error message, just skip this link
                print("loading error. opening next page (or link).")
                continue

            time_waited=0
            while(len(driver.find_elements_by_class_name("csgofloat-itemfloat"))<100):#wait for 100 on page
                print("waiting for 100 skins on page")
                time.sleep(0.25)
                time_waited = time_waited + 1
                if(time_waited % 120 == 0):
                    driver.get(links[l])
                    print("waited for 30 seconds. reloading page.")
                    
            tries = 0
            too_many_triess = False
            while(True):
                skins_arr = driver.find_elements_by_class_name("csgofloat-itemfloat")
                all_loaded = True
                for k in range(100):
                    if(skins_arr[k].is_displayed()==False):
                        all_loaded = False
                        print("something is wrong with visibility. checking again")
                        time.sleep(0.25)
                        tries = tries+1
                        break
                if(tries>=10):
                    print("too many tries. opening next tab")
                    too_many_triess = True
                    break
                if(all_loaded==True):
                    print("all 100 floats are visible")
                    break
            if(too_many_triess == False): # next part works if there is no error with visibility
                time.sleep(0.2)
                floats_elements = driver.find_elements_by_class_name("csgofloat-itemfloat")
                floats = []
                for f in floats_elements:
                    if(len(f.text.split())!=2): # check for preventing error "list index out of range"
                        floats.append(1.0)
                    else:
                        floats.append(float(f.text.split()[1]))
                print(floats)

                prices_elements = driver.find_elements_by_class_name("market_listing_price_with_fee")
                prices = []
                for p in prices_elements:
                    prices.append(priceSTR_to_float(p.text))
                print(prices)

                buttons = driver.find_elements_by_class_name("item_market_action_button")

                assert len(floats)==len(prices), "number of all floats, prices is not equal"

                while(True):
                    buy_error = False
                    for i in range(len(floats)): # for each skin
                        if(floats[i]<=max_floats[l]):
                            if(prices[i]!="Продано!"):
                                if(prices[i]<=max_prices[l]):
                                    buttons[i].click()
                                    WebDriverWait(driver, 60).until(expected_conditions.visibility_of_element_located((By.ID, "market_buynow_dialog_accept_ssa")))
                                    if(driver.find_element(By.ID,"market_buynow_dialog_accept_ssa").is_selected()==False):
                                        driver.find_element(By.ID,"market_buynow_dialog_accept_ssa").click()
                                    driver.find_element(By.ID,"market_buynow_dialog_purchase").click()
                                    while(driver.find_element_by_id("market_buynow_dialog_error_text").is_displayed()==False and driver.find_element_by_id("market_buynow_dialog_viewinventory").is_displayed()==False):
                                        time.sleep(0.25)
                                    if(driver.find_element_by_id("market_buynow_dialog_error_text").is_displayed()==True):
                                        buy_error = True
                                        print("***Not bought! steam error")
                                    else:
                                        print("***Skin was bought! Float:"+str(floats[i])+". Price:"+str(prices[i])+"***")
                                    driver.find_element_by_class_name("with_label").click();#close
                                    time.sleep(0.25)
                    if(buy_error == True):
                        continue
                    else:
                        break
                    
            #opening next tab
            searchResults_end = driver.find_element_by_id("searchResults_end").text
            driver.find_element_by_id("searchResults_btn_next").click() # next tab
            seconds = 0
            waiting_for_too_long = False
            while(len(driver.find_elements_by_id("searchResults_end"))==0 or searchResults_end == driver.find_element_by_id("searchResults_end").text):
                time.sleep(0.5)
                seconds = seconds + 1
                print("waiting for next tab to load")
                if(seconds%20==0):
                    print("waited for 10 seconds. clicking 'next tab' button again")
                    driver.find_element_by_id("searchResults_btn_next").click() # next tab
                if(seconds%120==0):
                    print("one minute passed. opening next link.")
                    waiting_for_too_long = True
                    break
            if(waiting_for_too_long == True):
                break
            WebDriverWait(driver, 60).until(expected_conditions.visibility_of_element_located((By.CLASS_NAME, "market_listing_price_with_fee")))
                    
#https://chrome.google.com/webstore/detail/csgofloat-market-checker/jjicbefpemnphinccgikpdaagjebbnhg?hl=uk







