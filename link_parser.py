import os

def main():
    for file in os.listdir('amazon-links-new'):
        supplement_name = file
        with open('amazon-links-new/' + file) as f:
            content = f.readlines()
        content = [x.strip() for x in content]
        f_write = open('asins-new/' + supplement_name, 'w')
        for link in content:
            asin_idx = link.find('dp/') + 3
            asin=link[asin_idx:asin_idx+10]
            f_write.write(asin+'\n')
if __name__ == '__main__':
    main()
