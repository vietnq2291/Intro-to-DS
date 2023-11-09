from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

from Clean_data import clean_data

def get_data(url)->list:
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0")

    driver = webdriver.Firefox(options=firefox_options)
    driver.get(url)

    hotels = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='Zvwhrc']")))

    data = []
    for hotel in hotels:
        hotel_name = hotel.find_element(By.XPATH, ".//h2[@class='BgYkof ogfYpf ykx2he']").text

        try:
            link_element = hotel.find_element(By.XPATH, ".//a[contains(@class, 'spNMC lRagtb')]")
            link_element.click()
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@class='Svr5cf bKhjM']")))

            reviews = driver.find_elements(By.XPATH, ".//div[@class='Svr5cf bKhjM']")

            enoughReviews = False
            count = 0

            while True:
                reviews = driver.find_elements(By.XPATH, ".//div[@jsname='Pa5DKe']//div[@class='Svr5cf bKhjM']")

                for review in reviews:
                    try:
                        review_text = review.find_element(By.XPATH, ".//div[@class='OlkcBc']//div[@class='K7oBsc']").text
                        review_rating = review.find_element(By.XPATH, ".//div[@class='GDWaad']").text

                        row = [hotel_name, review_text, review_rating]
                        data.append(row)

                        ### max 200 reviews for each Hotel
                        count += 1
                        if count > 1000:
                            enoughReviews = True
                            break
    

                    except Exception as e:
                        print("Error: ", e)
                        pass
                    
                if enoughReviews == True:
                    break
                # Scrolle to the next elem (jsname='Pa5DKe')
                try:
                    js_scroll = "window.scrollBy(0, 4000);"
                    driver.execute_script(js_scroll)
                    time.sleep(1)
                    # I need the upscroll the reload the new 'Pa5DKe' class
                    driver.execute_script("window.scrollBy(0, -100);")
                    driver.execute_script("window.scrollBy(0, 4000);")

                except Exception as e:
                    print("no more target element ", e)
                    break
        
        except Exception as e:
            print("Error: ", e)
            pass
        
        driver.back()

    driver.quit()
    return data

def create_csv_file(data):
    with open('data.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for row in data:
            writer.writerow(row)

def main():
    data = get_data("https://www.google.com/travel/search?q=london&ts=CAEaHBIaEhQKBwjnDxALGBASBwjnDxALGBEYATICEAAqBwoFOgNWTkQ&ved=0CAAQ5JsGahcKEwig0oXFsLGCAxUAAAAAHQAAAAAQOw&ictx=3&qs=CAAgACgA&ap=MAA")

    data = clean_data(data)

    create_csv_file(data)

if __name__ == '__main__':
     main()