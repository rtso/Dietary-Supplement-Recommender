from lxml import html
from selenium import webdriver
import requests

rankings_page = requests.get("https://labdoor.com/rankings")
rankings_tree = html.fromstring(rankings_page.content)
rankings_links = rankings_tree.xpath('//a[@class="rankingsListItemLink"]/@href')

print(rankings_links)
for i in range(22, len(rankings_links)):
    supplement_page = requests.get("https://labdoor.com" + rankings_links[i])
    supplement_name = rankings_links[i][10:]
    supplement_tree = html.fromstring(supplement_page.content)
    product_links = supplement_tree.xpath('//a[@class="categoryListItemLink"]/@href')
    print(product_links)
    with open('amazon-links/' + supplement_name + '.txt', 'w') as file:
        for j in range(0, len(product_links)):
            browser = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'])
            browser.get("https://labdoor.com" + product_links[j])
            product_tree = html.fromstring(browser.page_source)
            review_link = product_tree.xpath('//section[@id="shopModule"]//a[contains(text(), "Amazon USA")]/@href')
            if len(review_link) > 0:
                print(review_link[0])
                file.write(review_link[0] + '\n')
            browser.quit()

