from lxml import html
import os

from scraper import Scraper


class ScraperPdfWj(Scraper):

    SCRAPE_URL_LIST = [
        'https://gkisalatiga.org/category/warta-jemaat',
        'https://gkisalatiga.org/category/warta-jemaat/page/2',
    ]
    
    def __init__(self):
        super().__init__()
        self.api_key = os.environ['GDRIVE_API_KEY']
    
    def run(self):
        super().run()

        # Preamble logging.
        print('Beginning the automation script for updating data: Warta Jemaat')

        # Preparing the scrape result arrays.
        s1, s2, s3, s4, s5, s6, s7 = [], [], [], [], [], [], []

        # Iterating through every scraping URL list.
        for l in self.SCRAPE_URL_LIST:
            print(f'Getting the URL: {l} ...')
            r = self.rq.get(l)
            c = html.fromstring(r.content)

            base_xpath = '//header[@class="entry-header"]'

            # The scraped post page links.
            current_pages = c.xpath(base_xpath + '/h1[@class="entry-title"]/a/@href')
            s1.extend(current_pages)

            # The scraped church news title.
            s2.extend(c.xpath(base_xpath + '/h1[@class="entry-title"]/a/text()'))

            # The scraped post upload date.
            s3.extend(c.xpath(
                base_xpath +
                '/div[@class="entry-meta"]/span[@class="posted-on"]//time[@class="entry-date published"]/@datetime'
            ))

            print('Now retrieving the Google Drive links and thumbnails ...')
            for m in current_pages:
                print(f'Iterating: {m}')

                r = self.rq.get(m)
                c = html.fromstring(r.content)
                u = c.xpath('//div[@id="primary"]//iframe/@src')[0]
                print(f'--- Retrieved the URL: {u}')
                s4.append(u)

                a = c.xpath('//img[@class="attachment-post-thumbnail size-post-thumbnail wp-post-image"]/@src')
                if len(a) > 0:
                    t = a[0]
                else:
                    t = ''
                print(f'--- Retrieved the thumbnail: {t}')
                s5.append(t)

                # Retrieve the Google Drive file id.
                file_id = self.get_gdrive_file_id(u)
                s6.append(file_id)

                # Obtaining file size using GDrive API V3.
                try:
                    size = self.get_gdrive_file_size(file_id)
                    print(f'--- Obtained file size: {size}')
                except Exception as e:
                    size = '- MB'
                    print(f'--- [ERROR] ::: {e}')
                s7.append(size)

        # Resetting the JSON node.
        self.json_data['data']['pdf']['wj'] = []
        # Assumes identical s1, s2, s3, ... list size.
        # Writes the scraped data into the JSON file.
        print(f'Got length: {len(s1)}, {len(s2)}, {len(s3)}, {len(s4)}, {len(s5)}')
        print('Morphing the JSON data ...')
        for i in range(len(s1)):
            print(f'Writing data no. {i}: {s2[i]}')
            self.json_data['data']['pdf']['wj'].append({
                'title': s2[i],
                'date': s3[i].split('T')[0].strip(),
                'link': s4[i],
                'post-page': s1[i],
                'thumbnail': s5[i],
                'id': s6[i],
                'size': s7[i],
            })

        # Write changes.
        super().write(write_msg='pdf/wj')

        # Finalizing the script.
        super().finish()

    @staticmethod
    def get_gdrive_file_id(url: str):
        # Convert GDrive URL to fileId
        file_id = url.replace('/preview', '')
        file_id = file_id.replace('/edit', '')
        file_id = file_id.replace('/view', '')
        file_id = file_id.replace('/preview', '')
        file_id = file_id.replace('http://drive.google.com/file/d/', '')
        file_id = file_id.replace('https://drive.google.com/file/d/', '')
        file_id = file_id.replace('/', '')

        return file_id

    def get_gdrive_file_size(self, file_id):
        rest_node = 'https://www.googleapis.com/drive/v3/files'

        # Posting query.
        r = self.rq.get(rest_node + f'/{file_id}?key={self.api_key}&fields=*')
        j = r.json()

        # Convert to MB.
        size_in_bytes = int(j['size'])
        size_in_mb = '%.2f' % (size_in_bytes * 0.000001)

        return f'{size_in_mb} MB'


if __name__ == "__main__":
    scraper = ScraperPdfWj()
    scraper.run()
