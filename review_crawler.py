from lxml import html
import json, requests, random
from time import sleep

with open('useragent-strings.txt', 'r') as file:
    useragent_strings = file.read().split('\n')


def parse_review(asin):
    try:
        # Add a random user agent
        page = requests.get('https://www.amazon.com/product-reviews/' + asin, headers = {'User-Agent': random.choice(useragent_strings)})
        parser = html.fromstring(page.content)
        num_pages = int(parser.xpath('//li[@data-reftag="cm_cr_arp_d_paging_btm"][last()]/a/text()')[0])
        print('num pages: ', num_pages)
        reviews_list = []
        for i in range(num_pages):
            page = requests.get('https://www.amazon.com/product-reviews/' + asin + '?pageNumber=' + str(i))
            parser = html.fromstring(page.content)
            reviews = parser.xpath('//*[contains(@id, "customer_review")]')
            for review in reviews:
                info_dict = {}
                rating = review.xpath('.//i[@data-hook="review-star-rating"]//text()')[0]
                title = review.xpath('.//a[@data-hook="review-title"]//text()')[0]
                body = review.xpath('.//span[@data-hook="review-body"]//text()')[0]
                helpful = review.xpath('.//span[@data-hook="helpful-vote-statement"]//text()')
                if helpful:
                    helpful = helpful[0]
                else:
                    helpful = ''
                info_dict['rating'] = rating
                info_dict['title'] = title
                info_dict['body'] = body
                info_dict['helpful'] = helpful
                reviews_list.append(info_dict)
        return reviews_list
    except:
        print("Error")


def main():
    test = parse_review('B0011FY9AU')
    with open("json_file.json", "w") as json_file:
        json.dump(test, json_file)

if __name__ == '__main__':
    main()