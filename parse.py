#!/usr/bin/env python

import argparse
import settings
from phantomjstest.parser import PhantomJSParser


def main():

    print('Starting parser...')

    parser = argparse.ArgumentParser()
    parser.add_argument("search_query", nargs='+')
    args = parser.parse_args()
    search_query = ' '.join(args.search_query)
    print('Search query: ' + search_query)

    parser = PhantomJSParser(settings.AMAZON_LOGIN, settings.AMAZON_PASSWORD)
    parser.parse(search_query)

if __name__ == "__main__":
    main()

