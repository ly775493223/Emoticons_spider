import time
import pymongo
import selenium
from lxml import etree
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from splinter import browser

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)
driver.get('https://www.jd.com')
def search():
    try:
        element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#key")))
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#search > div > div.form > button")))
        element.send_keys('美食')
        submit.click()
        page = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"#J_bottomPage > span.p-skip > em:nth-child(1) > b")))
        return page.text
    except TimeoutException:
        search()

def next_page(next_number):
    try:
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#J_bottomPage > span.p-skip > input")))
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#J_bottomPage > span.p-skip > a")))
        input.clear()
        input.send_keys(next_number)
        submit.click()
        html = driver.page_source
        get_products(html)
        time.sleep(1)
        # wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,'#J_bottomPage > span.p-num > a.curr',str(next_number))))

    except selenium.common.exceptions.StaleElementReferenceException or selenium.common.exceptions.ElementNotInteractableException or TimeoutException:
        next_page(next_number)

def get_products(html):
    page = etree.HTML(html)
    items = page.xpath('//ul[@class="gl-warp clearfix"]/li')[1:]
    for item in items:
        product = {
            'img':item.xpath('.//@src'),
            'price':item.xpath('.//i/text()')[0],
            'title':item.xpath('./div/div[@class="p-name p-name-type-2"]//@title'),
            'shop':item.xpath('./div/div/span/a/@title'),
        }
        save_info(product)

def save_info(result):
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['mydb']
    try:
        if db['jd_products'].insert(result):
            print('存储成功')
    except Exception:
        print('存储失败')

def main():
    total = int(search())
    for i in range(2,total):
        next_page(i)

if __name__ == "__main__":
    main()
