import pickle
import sys
from os import listdir
from nltk.corpus import words
from review_crawler import Review

eng_words = set(words.words())


def load_reviews(path):
    reviews_str = ''
    for review in list(pickle.load(open(path, 'rb'))):
        try:
            reviews_str += review['body']
        except TypeError:
            reviews_str += review.body
    return reviews_str.lower()


def strip_punctuation(body):
    return body.replace('.', '').replace(',', '').replace('  ', ' ')


def spell_check(word):
    return word in eng_words


def pickle_to_str(path):
    reviews = load_reviews(path)
    reviews = strip_punctuation(reviews)
    tmp = ''
    for word in reviews.split(' '):
        if spell_check(word):
            tmp += word + ' '
    return tmp


def main():
    if len(sys.argv) is not 3:
        print('Usage: convert_to_meta.py <review path> <output file>')
        return
    dir_path = sys.argv[1]
    output_name = sys.argv[2]
    fd = open(output_name, 'w')
    for file in listdir(dir_path):
        if file.endswith('.p'):
            print('Converting', file)
            fd.write(pickle_to_str(dir_path + '/' + file) + '\n')
    fd.close()


if __name__ == '__main__':
    main()
