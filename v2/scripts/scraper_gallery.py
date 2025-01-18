from google.oauth2 import service_account
from googleapiclient.discovery import build
import copy
import json
import os
import sys

from scraper import Scraper

def do_add():
    input('Masukkan Google Drive V3 API Key: ')
    input('Masukkan ID Folder Google Drive: ')
    input('Sebutkan tahun: ')

def do_delete():
    pass

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
    
    def __init__(self):
        super().__init__()
        self.api_key = None
    
    def scrape(self):
        """ Scrape the Google Drive folder content. Return the JSON object of folder list. """
        
        # Build the credential using the provided Service Account key file.
        creds = service_account.Credentials.from_service_account_info(
            json.loads(self.api_key, strict=False),
            scopes=self.GOOGLE_DRIVE_SCOPES
        )
        
        # Attempt to upload the requested file to Google Drive.
        # Error-catching is done at level of the method which called this function.
        service = build('drive', 'v3', credentials=creds)
        
        # Return data fields that we desire.
        # SOURCE: https://developers.google.com/drive/api/reference/rest/v3/files
        fields = 'nextPageToken, files(id, name, createdTime, mimeType, shortcutDetails)'
        
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
            results = service.files().list(
                q=f"'{self.ROOT_FOLDER_ID}' in parents",
                fields=fields,
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
                        results = service.files().list(
                            q=f"'{folder_id}' in parents",
                            fields=fields,
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

        return json.dumps(list_layer_2)
    
    def run(self):
        super().run()

        # Preamble logging.
        print('Beginning the automation script for updating data: Gallery')

        # The YouTube v3 API key.
        print('Retrieving the API KEY secrets ...')
        self.api_key = os.environ['GDRIVE_API_KEY']
        
        print(self.scrape())

if __name__ == '__main__':
    scraper = ScraperGallery()
    scraper.run()
    sys.exit(0)
