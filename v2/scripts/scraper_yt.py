from datetime import datetime as dt
from lxml import html
import os

from scraper import Scraper


# 2-digit zero-padding.
def zero_pad(num):
    if len(str(num)) == 0:
        return '00'
    elif len(str(num)) == 1:
        return f'0{num}'
    else:
        return num


class ScraperYT(Scraper):

    # The GKI Salatiga YouTube channel ID
    MAIN_CHANNEL_ID = 'UC5cn_kPPnf-VUYFnB0N7MZg'
    
    def __init__(self):
        super().__init__()
        self.api_key = None

    def run(self):
        super().run()

        # Preamble logging.
        print('Beginning the automation script for updating data: YouTube')

        # The YouTube v3 API key.
        print('Retrieving the API KEY secrets ...')
        self.api_key = os.environ['YT_API_KEY']

        # Iterating through every registered GKI Salatiga+ playlist.
        for i in range(len(self.json_data['data']['yt'])):
            # Detecting the type of playlist.
            if self.json_data['data']['yt'][i]['type'] == 'rss':
                title_keyword = self.json_data['data']['yt'][i]['rss-title-keyword']

                # Obtaining the latest contents.
                self.json_data['data']['yt'][i]['content'] = self.scrape_yt_rss(title_keyword, self.MAIN_CHANNEL_ID)

            elif self.json_data['data']['yt'][i]['type'] == 'regular':
                playlist_id = self.json_data['data']['yt'][i]['playlist-id']

                # Obtaining the latest contents.
                self.json_data['data']['yt'][i]['content'] = self.scrape_yt_regular(playlist_id)

            # Updating metadata.
            now = dt.now()
            current_date = f'{now.year}-{zero_pad(now.month)}-{zero_pad(now.day)}'
            self.json_data['data']['yt'][i]['last-update'] = current_date

        # Write changes.
        super().write(write_msg='yt')

        # Finalizing the script.
        super().finish()

    def scrape_yt_regular(self, playlist_id: str):
        # Preparing the request queries
        part = 'snippet'
        max_results = 30

        # The Google API v3 bridge.
        bridge = 'https://www.googleapis.com/youtube/v3/playlistItems'

        # SOURCE: https://stackoverflow.com/a/55207539
        print(f'Getting the video data for playlist: {playlist_id} ...')
        r = self.rq.get(bridge + f'?key={self.api_key}&part={part}&playlistId={playlist_id}&maxResults={max_results}')

        # The scraped YT video titles.
        s1 = []

        # The scraped YT video ID.
        s2 = []

        # The scraped YT upload date.
        s3 = []

        # The scraped YT video description.
        s4 = []

        # The scraped YT video URL.
        s5 = []

        # The scraped YT video thumbnail.
        s6 = []

        # Parsing the response JSON string.
        i = 0
        for a in r.json()['items']:
            video_id = a['snippet']['resourceId']['videoId']
            print(f'--- Iteration {i}; obtaining metadata for video ID: {video_id}')

            if a['snippet']['thumbnails'] == {}:
                print('..... Cannot retrieve video thumbnail because the video is private. Skipping ...')
                i += 1
                continue

            s1.append(a['snippet']['title'])
            s2.append(video_id)
            s3.append(a['snippet']['publishedAt'].split('T')[0])
            s4.append(a['snippet']['description'].strip())
            s5.append(f'https://www.youtube.com/watch?v={video_id}')
            s6.append(a['snippet']['thumbnails']['high']['url'])

            i += 1

        # Assumes identical s1, s2, s3, ... list size.
        # Writes the scraped data into the JSON file.
        print(f'Got length: {len(s1)}, {len(s2)}, {len(s3)}, {len(s4)}, {len(s5)}, {len(s6)}')
        print('Morphing the JSON data ...')
        j = []
        for i in range(len(s1)):
            print(f'Writing data no. {i}: {s1[i]}')
            j.append({
                'title': s1[i],
                'date': s3[i],
                'desc': s4[i],
                'link': s5[i],
                'thumbnail': s6[i],
            })

        return j

    def scrape_yt_rss(self, title_keyword: str, channel_id: str):
        # SOURCE: https://stackoverflow.com/a/55207539
        print(f'Getting the XML RSS feed: {channel_id} ...')
        r = self.rq.get(f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}')
        c = html.fromstring(r.content)

        # The scraped YT video titles.
        s1 = [l.strip() for l in c.xpath('//entry/title/text()')]

        # The scraped YT video ID.
        s2 = [l.split(':')[2] for l in c.xpath('//entry/id/text()')]

        # The scraped YT upload date.
        s3 = [l.split('T')[0] for l in c.xpath('//entry/published/text()')]

        # The scraped YT video description.
        # SOURCE: https://stackoverflow.com/questions/5239685/xml-namespace-breaking-my-xpath
        s4 = [l.strip() for l in c.xpath('//entry//*[local-name()="media:description"]/text()')]

        # The scraped YT video URL.
        s5 = [l.strip() for l in c.xpath('//entry/link/@href')]

        # The scraped YT video thumbnail.
        s6 = [l.strip() for l in c.xpath('//entry//*[local-name()="media:thumbnail"]/@url')]

        # Assumes identical s1, s2 and s3 list size.
        # Writes the scraped data into the JSON file.
        print(f'Got length: {len(s1)}, {len(s2)}, {len(s3)}, {len(s4)}, {len(s5)}, {len(s6)}')
        print('Morphing the JSON data ...')
        j = []
        for i in range(len(s1)):
            if s1[i].lower().__contains__(title_keyword.lower()):
                print(f'Writing data no. {i}: {s1[i]}')
                j.append({
                    'title': s1[i],
                    'date': s3[i],
                    'desc': s4[i],
                    'link': s5[i],
                    'thumbnail': s6[i],
                })

        return j


if __name__ == "__main__":
    scraper = ScraperYT()
    scraper.run()
