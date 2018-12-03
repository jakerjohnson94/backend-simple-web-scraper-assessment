#!/usr/bin/env python2
__author__ = 'Jake Johnson'

import sys
import argparse
import requests
import re
from HTMLParser import HTMLParser


class HTML_Info_Parser(HTMLParser):
    phone_list, email_list, url_list = [], [], []

  # ensure proper formatting and remove whitespace
    def format_data(self, *strings):
        for string in strings:
            string = str(string.encode('ascii')).strip()
        return strings

  # sort list and remove duplicates
    def format_list(self, lst):
        return sorted(list(set(lst)))

    def handle_data(self, data):
        """ find regex matches and format data for output """
        format_list, format_data = self.format_list, self.format_data

        # ensure images do not get scraped as emails
        invalid_domains = ['png', 'jpg', 'gif']

        regex = {
            'email': r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",
            'phone': r"1?\W*([2-9][0-8][0-9])\W*([2-9][0-9]{2})\W*([0-9]{4})(\se?x?t?(\d*))?",
            'url': r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))[^\)\"';\s]+"
        }

        # search raw html for regex matches
        phone_matches, email_matches, url_matches = re.findall(
            regex['phone'], data), re.findall(regex['email'], data), re.findall(regex['url'], data)

        # format lists for output if they exist
        [self.phone_list.append(
            '({}){}-{}'.format(*format_data(phone[0], phone[1], phone[2])))
         for phone in format_list(phone_matches) if phone_matches]

        [self.email_list.append(*format_data(email))
         for email in format_list(email_matches) if email_matches and email.split('.')[-1] not in invalid_domains]

        [self.url_list.append(*format_data(url))
         for url in format_list(url_matches) if url_matches]


def scrape_html(url):
    html_req = requests.get(url)
    parser = HTML_Info_Parser()
    parser.feed(html_req.text)

    phones, emails, urls = parser.phone_list, parser.email_list, parser.url_list
    # output
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
