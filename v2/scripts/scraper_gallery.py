from google.oauth2 import service_account
from googleapiclient.discovery import build
import copy
import json
import os
import sys

from scraper import Scraper


class ScraperGallery(Scraper):
    
    # The Google Drive parent/root folder ID.
    ROOT_FOLDER_ID = '1VmebLaBcFEZdebSkVKInhuxz_huoIWkw'
    
    # The Google Drive API scopes.
    GOOGLE_DRIVE_SCOPES = [
        'https://www.googleapis.com/auth/docs',
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.appdata',
        'https://www.googleapis.com/auth/drive.apps.readonly',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.meet.readonly',
        'https://www.googleapis.com/auth/drive.metadata',
        'https://www.googleapis.com/auth/drive.metadata.readonly',
        'https://www.googleapis.com/auth/drive.photos.readonly',
        'https://www.googleapis.com/auth/drive.readonly',
    ]
    
    @staticmethod
    def json_date_to_locale(s):
        """ Converts, e.g., 2024-01-24 to 24 Januari 2024. """
        
        month_locales = {
            '01': 'Januari',
            '02': 'Februari',
            '03': 'Maret',
            '04': 'April',
            '05': 'Mei',
            '06': 'Juni',
            '07': 'Juli',
            '08': 'Agustus',
            '09': 'September',
            '10': 'Oktober',
            '11': 'November',
            '12': 'Desember',
        }
        
        a = s.split('.')
        return str(int(a[2])) + ' ' + month_locales[a[1]] + ' ' + a[0]
    
    def __init__(self):
        super().__init__()
        self.api_key = os.environ['GDRIVE_API_KEY']
        
        # Build the credential using the provided Service Account key file.
        self.creds = service_account.Credentials.from_service_account_info(
            json.loads(self.api_key, strict=False),
            scopes=self.GOOGLE_DRIVE_SCOPES
        )
        
        # Attempt to upload the requested file to Google Drive.
        # Error-catching is done at level of the method which called this function.
        self.service = build('drive', 'v3', credentials=self.creds)
        
        # Return data fields that we desire.
        # SOURCE: https://developers.google.com/drive/api/reference/rest/v3/files
        self.fields = 'nextPageToken, files(id, name, createdTime, modifiedTime, mimeType, shortcutDetails)'
    
    def scrape(self):
        """ Scrape the Google Drive folder content. Return the JSON object of folder list. """
        
        # Whether to only scrape the first page.
        only_first_page = False
        
        # The page token.
        page_token = None
        
        # Stores all items from all pages (in the root folder).
        list_layer_1 = []
        
        # Call the Drive v3 API to upload a file
        print('+ Enlisting the root folder...')
        while True:
            print('+ Still scraping ...')
            results = self.service.files().list(
                q=f"'{self.ROOT_FOLDER_ID}' in parents",
                fields=self.fields,
                pageToken=page_token
            ).execute()
            items = results.get('files', [])
            
            # Appending to all items.
            list_layer_1.extend(items)
        
            # Go to next page.
            page_token = results.get('nextPageToken', None)
            if page_token is None or only_first_page:
                break
        
        # Stores all items from all pages (in subfolders).
        list_layer_2 = []
        
        # Enlisting folders' shortcut content.
        for a in list_layer_1:
            if a['mimeType'] == 'application/vnd.google-apps.folder':
                if a['name'][:4].isdigit():
                    print(f'+ Enlisting folder: {a["name"]}...')
                    
                    # Enlisting this folder.
                    folder_id = a['id']
                    
                    # Temporary list.
                    list_temp = []
        
                    # Call the Drive v3 API to upload a file
                    while True:
                        print('+ Still scraping ...')
                        results = self.service.files().list(
                            q=f"'{folder_id}' in parents",
                            fields=self.fields,
                            pageToken=page_token
                        ).execute()
                        items = results.get('files', [])
                        
                        # Appending to all items.
                        list_temp.extend(items)
                    
                        # Go to next page.
                        page_token = results.get('nextPageToken', None)
                        if page_token is None or only_first_page:
                            break
                    
                    # Integrate the scraped content.
                    j = copy.deepcopy(a)
                    j['scraped_content'] = copy.deepcopy(list_temp)
                    list_layer_2.append(j)
        
        # Sort the resulting dict.
        sorted_list_layer_2 = sorted(list_layer_2, key=lambda item: item['name'])
        
        return sorted_list_layer_2
    
    def run(self):
        super().run()

        # Preamble logging.
        print('Beginning the automation script for updating data: Gallery')

        # The YouTube v3 API key.
        print('Retrieving the API KEY secrets ...')
        self.api_key = os.environ['GDRIVE_API_KEY']
        
        # Get the list of images.
        j = self.scrape()
        
        # Building the root, per-year "album-data" object.
        root_year = {}
        
        # Transforming each album.
        for a in j:
            print(f'Transforming album: {a["name"]} ...')
            
            real_name = a['name'][13:]
            date_locale = self.json_date_to_locale(a['name'][:10])
            date_year = a['name'][:4]
            desc = f'Foto-foto dokumentasi {real_name} yang dilaksanakan pada {date_locale}.'
            
            # Temporary sub-album data.
            sub_data = {
                'folder_id': a['id'],
                'last_update': a['modifiedTime'].split('T')[0],
                'featured_photo_id': a['scraped_content'][0]['id'] if a['scraped_content'].__len__() > 0 else '',
                'story': desc,
                'title': real_name,
                'event_date': a['name'][:10],
                'photos': []
            }
            
            # Now add individual photos.
            for b in a['scraped_content']:
                # Skip shortcut of shortcuts.
                if b['shortcutDetails']['targetMimeType'] == 'application/vnd.google-apps.shortcut':
                    print('Skipping shortcut of shortcuts ...')
                    continue
                
                sub_data['photos'].append(
                    {
                        'id': b['shortcutDetails']['targetId'],
                        'name': b['name'],
                        'date': b['modifiedTime'].split('T')[0],
                    }
                )
            
            # Integrate this album with all albums data.
            if date_year not in root_year.keys():
                root_year[date_year] = []
            
            root_year[date_year].append(sub_data)
        
        # Merge with the JSON file.
        out = []
        for b in root_year.keys():
            title = f'Kilas Balik GKI Salatiga Tahun {b}'
            album_data = sorted(root_year[b], key=lambda item: item['event_date'])
            out.append(
                {
                    'title': title,
                    'album-data': copy.deepcopy(album_data)
                }
            )
            
        self.json_data_gallery['gallery'] = copy.deepcopy(out)
        
        # Write changes.
        super().write()

        # Finalizing the script.
        super().finish()

if __name__ == '__main__':
    scraper = ScraperGallery()
    scraper.run()
    sys.exit(0)
