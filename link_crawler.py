from lxml import html
from selenium import webdriver
import requests, os, random

with open('useragent-strings.txt', 'r') as file:
    useragent_strings = file.read().split('\n')


def crawl_urls():
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


def get_asins(read_filename, write_filename, line_index):
    print(write_filename)
    with open(read_filename, 'r') as read_file, open(write_filename, 'a') as write_file:
        for i in range(line_index):
            read_file.readline()
        for url in read_file:
            print(url)
            try:
                page = requests.get(url, headers = {'User-Agent': random.choice(useragent_strings)})
                page_tree = html.fromstring(page.content)
                # print(page.content)
                asin = page_tree.xpath('//*[@id="ftSelectAsin"]/@value')[0]
                print(line_index)
                print(asin)
                write_file.write('http://amazon.com/dp/' + asin + '\n')
            except IndexError:
                print('Stopped at index ', line_index)
                return line_index
            line_index += 1


def main():
    """
    To make sure the crawler handles exceptions gracefully, anytime the crawler runs into an exception with the HTML,
    the file and line numbers last crawled are logged in status.txt to be the starting point of the next crawl.
    """
    with open('status.txt', 'r') as status_file:
        file_index = int(status_file.readline())
        line_index = int(status_file.readline())
    print(file_index, line_index)
    for file in os.listdir('amazon-links')[file_index:]:
        supplement_name = file[:-4]
        stop_index = get_asins('amazon-links/' + file, 'asins/' + supplement_name + '-asins.txt', line_index)
        if stop_index and stop_index > -1:
            with open('status.txt', 'w') as status_file:
                status_file.write(str(file_index) + '\n')
                status_file.write(str(stop_index))
                return
        file_index += 1
        line_index = 0


if __name__ == '__main__':
    main()


