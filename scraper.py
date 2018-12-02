#!/usr/bin/env python2
__author__ = 'Jake Johnson'

import sys
import argparse
import requests
import re
from HTMLParser import HTMLParser

email_regex = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
phone_regex = r"1?\W*([2-9][0-8][0-9])\W*([2-9][0-9]{2})\W*([0-9]{4})(\se?x?t?(\d*))?"
url_regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))[^\)\"';\s]+"


class MyHTMLParser(HTMLParser):
    phone_list = []
    email_list = []
    url_list = []

    def handle_data(self, data):
        phone_matches = re.search(phone_regex, data)
        email_matches = re.findall(email_regex, data)
        url_matches = re.findall(url_regex, data)
        if phone_matches:
            self.phone_list.append('{} {}-{}'.format(phone_matches.group(1),
                                                     phone_matches.group(2), phone_matches.group(3)))
        if email_matches:
            for email in email_matches:
                self.email_list.append(email)
        if url_matches:
            for url in url_matches:
                self.url_list.append(url)

        # Convert list to ascii to avoid string formatting errors
        self.url_list = [x.encode('ascii') for x in self.url_list]


def get_html_source(url):
    r = requests.get(url)
    parser = MyHTMLParser()
    parser.feed(r.text)
    phones, emails, urls = list(set(parser.phone_list)), list(set(
        parser.email_list)), list(set(parser.url_list))
    print('\nPhone Numbers:\n' + '    '.join(phones))
    print('\nEmails:\n\n' + '   '.join(emails))
    print('\nURLs:\n\n' + '\n'.join(urls))


def main():
    parser = argparse.ArgumentParser(
        description='Print a list of relevant info from a URL')
    parser.add_argument('url',
                        help='a website URL to scrape data from')

    args = parser.parse_args()

    if args.url:
        get_html_source(args.url)


if __name__ == "__main__":
    main()
