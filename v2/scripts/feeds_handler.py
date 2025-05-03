import json
import time


class FeedsHandler(object):

    MAIN_FEEDS_SRC = 'v2/data/feeds.json'
    MAIN_FEEDS_SRC_MINI = 'v2/data/feeds.min.json'

    json_feeds_data = None

    def __init__(self):
        # Initializing the JSON objects.
        # Reading the data...
        with open(self.MAIN_FEEDS_SRC, 'r') as fi:
            self.json_feeds_data = json.load(fi)

    def update_feed_gallery(self):
        self.json_feeds_data['feeds']['last-gallery-update'] = int(time.time())
        self.sign_off()

    def update_feed_maindata(self):
        self.json_feeds_data['feeds']['last-main-update'] = int(time.time())
        self.sign_off()

    def update_feed_static(self):
        self.json_feeds_data['feeds']['last-static-update'] = int(time.time())
        self.sign_off()

    def sign_off(self):
        # Write the human-readable JSON file.
        with open(self.MAIN_FEEDS_SRC, 'w') as fo:
            json.dump(self.json_feeds_data, fo, indent=4)

        # Write the compactified JSON file.
        with open(self.MAIN_FEEDS_SRC_MINI, 'w') as fo:
            json.dump(self.json_feeds_data, fo, separators=(',', ':'))
