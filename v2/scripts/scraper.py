from datetime import datetime as dt
import copy
import json
import requests
import sys
import time

from feeds_handler import FeedsHandler


class Scraper(object):

    GALLERY_JSON_SRC = 'v2/data/gkisplus-gallery.json'
    GALLERY_JSON_SRC_MINI = 'v2/data/gkisplus-gallery.min.json'
    MAIN_JSON_SRC = 'v2/data/gkisplus-main.json'
    MAIN_JSON_SRC_MINI = 'v2/data/gkisplus-main.min.json'
    
    json_data_gallery = None
    _json_data_gallery_old = None
    json_data = None
    _json_data_old = None
    
    exit_code = None
    
    def __init__(self):
        print(f'[{self.__class__.__name__}] Initializing the scraper ...')
        self.t = dt.now()
        
        # Initializing the JSON objects.
        # Reading the data...
        with open(self.MAIN_JSON_SRC, 'r') as fi:
            self.json_data = json.load(fi)
            self._json_data_old = copy.deepcopy(self.json_data)
            
        with open(self.GALLERY_JSON_SRC, 'r') as fi:
            self.json_data_gallery = json.load(fi)
            self._json_data_gallery_old = copy.deepcopy(self.json_data_gallery)
        
        # Preparing the requests session.
        self.rq = requests.Session()

    def finish(self):
        """ Finalize the current scraper's session. """
        print(f'[{self.__class__.__name__}] Finished the scraper. Total script time: {dt.now() - self.t}')
        sys.exit(self.exit_code)
    
    def run(self):
        
        # This is supposed to be an abstract function.
        # Run your scraping code here.
        pass
    
    def write(self, write_msg='unspecified'):
        """ Handles the writing of (modified) JSON data to the main source. """
        
        # Check if there is no update.
        do_update_main, do_update_gallery = True, True
        
        if self.json_data['data'] == self._json_data_old['data']:
            do_update_main = False
        
        if self.json_data_gallery['gallery'] == self._json_data_gallery_old['gallery']:
            do_update_gallery = False
        
        # Checking the logic.
        if do_update_main or do_update_gallery:
            print(f'[{self.__class__.__name__}] Writing the scraper ...')
            
            # Update the feeds.
            feeds = FeedsHandler()
    
            # Handle the metadata administration.
            if do_update_main:
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
                
                feeds.update_feed_maindata()
            
            if do_update_gallery:
                self.json_data_gallery['meta']['last-actor'] = 'GITHUB_ACTIONS'
                self.json_data_gallery['meta']['last-update'] = int(time.time())
                self.json_data_gallery['meta']['update-count'] += 1
            
                # Write the human-readable JSON file.
                with open(self.GALLERY_JSON_SRC, 'w') as fo:
                    json.dump(self.json_data_gallery, fo, indent=4)
                
                # Write the compactified JSON file.
                with open(self.GALLERY_JSON_SRC_MINI, 'w') as fo:
                    json.dump(self.json_data_gallery, fo, separators=(',', ':'))
                
                feeds.update_feed_gallery()
            
            self.exit_code = 0
        
        else:
            print(f'[{self.__class__.__name__}] Not writing any file because there is no data change!')
            self.exit_code = 234
        