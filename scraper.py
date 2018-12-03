#!/usr/bin/env python2
import argparse
import requests
import re
from HTMLParser import HTMLParser

__author__ = 'Jake Johnson'


class HTML_Info_Parser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)

        self.phone_list = []
        self.email_list = []
        self.url_list = []
        self.regex = {
            'phone': r"\D(\(?\d{3})\D{0,3}(\d{3})\D{0,3}(\d{4})\D",
            'email': r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",
            'url': (r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]"
                    r"|(?:%[0-9a-fA-F][0-9a-fA-F]))[^\)\"';\s]+")
        }

    def handle_starttag(self, tag, attr):
        # scrape urls from specific html tags
        tag_dict = {'link': 'href', 'img': 'src',}
        if tag in tag_dict.keys():
            [self.url_list.append(v) for k,v in attr if k == tag_dict[tag]]

        # scrape phone numbers from link tags
        elif tag == 'a':
            [self.phone_list.append('({}){}-{}'.format(phone[0], phone[1], phone[2]))
            for k,v in attr if k == 'href' and re.search(self.regex['phone'], v)]
                    
         

    def handle_data(self, data):
        """ find regex matches and format data for output """
        regex = self.regex
        # ensure images do not get scraped as emails
        invalid_domains = ['png', 'jpg', 'gif']


        # search raw html for regex matches
        phone_matches = re.findall(regex['phone'], data)
        email_matches = re.findall(regex['email'], data)
        url_matches = re.findall(regex['url'], data)

        # format lists for output if they exist
        [self.phone_list.append(
            '({}){}-{}'.format(phone[0], phone[1], phone[2]))
         for phone in phone_matches if phone_matches]

        [self.email_list.append(email)
         for email in email_matches if email_matches and
         email.split('.')[-1] not in invalid_domains]

        [self.url_list.append(url)
         for url in url_matches if url_matches]



def format_list(ls):
    # sort list and remove duplicates
    return sorted(list(set(ls)))


def scrape_html(url):
    html_req = requests.get(url)
    parser = HTML_Info_Parser()
    parser.feed(html_req.text.encode('utf8'))

    phones, emails, urls = (format_list(parser.phone_list),
                            format_list(parser.email_list),
                            format_list(parser.url_list))

    # output
    print('Data found from {}: '.format(url))
    if phones:
        print('\nPhone Numbers:\n' + '\n'.join(phones))
    if emails:
        print('\nEmails:\n' + '\t'.join(emails))
    if urls:
        print('\nURLs:\n' + '\n'.join(urls))


def main():
    parser = argparse.ArgumentParser(
        description='Print a list of relevant info from a URL')
    parser.add_argument('url',
                        help='a website URL to scrape data from')
    args = parser.parse_args()

    if args.url:
        scrape_html(args.url)


if __name__ == "__main__":
    main()
