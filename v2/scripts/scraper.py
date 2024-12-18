from datetime import datetime as dt
import json
import requests
import time

from feeds_handler import FeedsHandler


class Scraper(object):

    MAIN_JSON_SRC = 'v2/data/gkisplus-main.json'
    MAIN_JSON_SRC_MINI = 'v2/data/gkisplus-main.min.json'
    
    json_data = None
    
    def __init__(self):
        print(f'[{self.__class__.__name__}] Initializing the scraper ...')
        self.t = dt.now()
        
        # Initializing the JSON objects.
        # Reading the data...
        with open(self.MAIN_JSON_SRC, 'r') as fi:
            self.json_data = json.load(fi)
        
        # Preparing the requests session.
        self.rq = requests.Session()

    def finish(self):
        """ Finalize the current scraper's session. """
        print(f'[{self.__class__.__name__}] Finished the scraper. Total script time: {dt.now() - self.t}')
    
    def run(self):
        
        # This is supposed to be an abstract function.
        # Run your scraping code here.
        pass
    
    def write(self, write_msg='unspecified'):
        """ Handles the writing of (modified) JSON data to the main source. """

        print(f'[{self.__class__.__name__}] Writing the scraper ...')

        # Handle the metadata administration.
        self.json_data['meta']['last-actor'] = 'GITHUB_ACTIONS'
        self.json_data['meta']['last-update'] = int(time.time())
        self.json_data['meta']['last-updated-item'] = str(write_msg)
        self.json_data['meta']['update-count'] += 1

        # Write the human-readable JSON file.
        with open(self.MAIN_JSON_SRC, 'w') as fo:
            json.dump(self.json_data, fo, indent=4)
        
        # Write the compactified JSON file.
        with open(self.MAIN_JSON_SRC_MINI, 'w') as fo:
            json.dump(self.json_data, fo, separators=(',', ':'))

        # Update the feeds.
        feeds = FeedsHandler()
        feeds.update_feed_maindata()
        