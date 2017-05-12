import pickle
import sys
import pandas
import re
from os import listdir
from nltk.corpus import words
from review_crawler import Review

# define the vocabulary
df = pandas.read_csv('fda_drugs_data.txt',delimiter='\t')
drug_words = set([item.lower().partition(" ")[0] for item in df['DrugName'].values.tolist()])
fd0 = open('conditions_list.txt')
health_words = set([item.lower() for item in fd0.read().split('\n')])
fd0.close()
eng_words = set(words.words())
all_words = eng_words.union(drug_words).union(health_words)

# define positive and negative reviews
neg_ratings = [1, 2]
pos_ratings = [3, 4, 5]

counts = [0, 0]

def convert_sentences(path, neg_corpus_fd, pos_corpus_fd):
    for review in list(pickle.load(open(path, 'rb'))):

        # get review text and rating from object
        try:
            review_str = review['body']
            review_rating = review['rating']
        except TypeError:
            review_str = review.body
            review_rating = review.rating

        # clean up
        review_str = review_str.lower()
        review_str = strip_punctuation(review_str)

        # spell check
        tmp = ''
        for word in review_str.split(' '):
            if spell_check(word):
                tmp += word + ' '
        if not tmp:
            continue

        # write sentence and label to output in MeTA corpus format
        if int(review_rating) in neg_ratings:
            neg_corpus_fd.write(tmp + ' ')
            counts[0] += 1
        elif int(review_rating) in pos_ratings:
            pos_corpus_fd.write(tmp + ' ')
            counts[1] += 1
    neg_corpus_fd.write('\n')
    pos_corpus_fd.write('\n')


def strip_punctuation(text):
    return text.replace('.','').replace(',', '').replace('!','').replace('\'','').replace('  ', ' ')


def spell_check(word):
    return word in all_words


def main():
    if len(sys.argv) is not 3:
        print('Usage: convert_to_meta_sentence.py <review path> <output file>')
        return
    dir_path = sys.argv[1]
    output_name = sys.argv[2]
    fd1 = open(output_name + '.neg.dat', 'w')
    fd2 = open(output_name + '.pos.dat', 'w')
    for file in listdir(dir_path):
        if file.endswith('.p'):
            print('Converting', file)
            convert_sentences(dir_path + '/' + file, fd1, fd2)
    fd1.close()
    fd2.close()
    print('Percent positive: ' + str(counts[1]/(counts[0]+counts[1])))

if __name__ == '__main__':
    main()
