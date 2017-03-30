from lxml import html
import simplejson
import requests
import random
import _pickle
import sys
import os
from collections import deque
from time import sleep


class Review:
    def __init__(self, rating, title, body, helpful):
        self.rating = rating
        self.title = title
        self.body = body
        self.helpful = helpful

url_queue_filename = 'queue.p'

with open('useragent-strings.txt', 'r') as file:
    useragent_strings = file.read().split('\n')

reviews_list = deque()
urls = deque()


def add_asin(asin):
    print(asin)
    # Add URLs to the queue for scraping
    page = requests.get('https://www.amazon.com/product-reviews/' + asin,
                        headers = {'User-Agent': random.choice(useragent_strings)})
    parser = html.fromstring(page.content)
    num_pages = parser.xpath('//li[@data-reftag="cm_cr_arp_d_paging_btm" or'
                             '@data-reftag="cm_cr_getr_d_paging_btm"][last()]/a/text()')
    if num_pages:
        num_pages = int(num_pages[0].replace(',', ''))
    else:
        # There is only one page of reviews
        num_pages = 1
    for i in range(1, num_pages + 1):
        urls.append('https://www.amazon.com/product-reviews/' + asin + '?pageNumber=' + str(i))


def get_reviews():
    num_reviews = 0
    try:
        while urls:
            url = urls[0]
            rl = deque()
            page = requests.get(url, headers = {'User-Agent': random.choice(useragent_strings)})
            parser = html.fromstring(page.content)
            reviews = parser.xpath('//*[contains(@id, "customer_review")]')
            if not reviews:
                print('No reviews found for', url)
                urls.popleft()
            for review in reviews:
                rating = review.xpath('.//i[@data-hook="review-star-rating"]//text()')[0]
                title = review.xpath('.//a[@data-hook="review-title"]//text()')[0]
                body = review.xpath('.//span[@data-hook="review-body"]//text()')
                if body:
                    body = body[0]
                else:
                    body = ''
                helpful = review.xpath('.//span[@data-hook="helpful-vote-statement"]//text()')
                if not helpful:
                    helpful = 0
                elif 'One' in helpful[0]:
                    helpful = 1
                else:
                    helpful = int(list(filter(str.isdigit, helpful[0]))[0])
                review_obj = Review(rating[0], title, body.replace('\n', ''), helpful)
                rl.append(review_obj)
                num_reviews += 1
            print('Got ', num_reviews, ' reviews')
            urls.popleft()
            reviews_list.extend(rl)
        # Queue is empty, remove queue.p file
        if os.path.exists(url_queue_filename):
            os.remove(url_queue_filename)
            print('Removed queue file')
    except:
        e = sys.exc_info()[0]
        print(e)
        print(e.args)
        print('Stopped at ', urls[0])
        with open('queue.p', 'wb') as url_queue_file:
            _pickle.dump(urls, url_queue_file)


def main():
    if not os.path.exists('reviews'):
        os.makedirs('reviews')
    asin_filename = sys.argv[1]
    supplement_name = asin_filename[6:-10]
    print(supplement_name)
    pkl_filename = 'reviews/' + supplement_name + '-reviews.p'

    # Load URL queue
    if os.path.exists(url_queue_filename):
        global urls
        with open(url_queue_filename, 'rb') as url_queue_file:
            urls = _pickle.load(url_queue_file, encoding='latin1')
        print('Loading ASIN queue')

        # Load reviews list
        if os.path.exists(pkl_filename):
            global reviews_list
            with open(pkl_filename, 'rb') as pkl_file:
                reviews_list = _pickle.load(pkl_file, encoding='latin1')
        print('Loaded pkl file')
    else:
        with open(asin_filename, 'r') as asin_file:
            for asin in asin_file:
                add_asin(asin.strip())
        print('ASINs loaded in queue')

    get_reviews()

    with open(pkl_filename, 'wb') as pkl_file:
        _pickle.dump(reviews_list, pkl_file)
    with open('reviews/' + supplement_name + '-reviews.json', 'w') as json_file:
        simplejson.dump([r.__dict__ for r in list(reviews_list)], json_file)
    print(len(reviews_list))

if __name__ == '__main__':
    main()
