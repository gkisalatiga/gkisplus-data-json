from copy import deepcopy
from lxml import html

from scraper import Scraper

# Map of months used in the website's instance.
months_map = {
    'jan': 1,
    'feb': 2,
    'mar': 3,
    'apr': 4,
    'may': 5,
    'jun': 6,
    'jul': 7,
    'aug': 8,
    'sep': 9,
    'oct': 10,
    'nov': 11,
    'dec': 12,
}

# Map of months in Indonesian
months_indonesian = [
    'Januari',
    'Februari',
    'Maret',
    'April',
    'Mei',
    'Juni',
    'Juli',
    'Agustus',
    'September',
    'Oktober',
    'November',
    'Desember',
]


# 2-digit zero-padding.
def zero_pad(num):
    if len(str(num)) == 0:
        return '00'
    elif len(str(num)) == 1:
        return f'0{num}'
    else:
        return num


class ScraperYKB(Scraper):

    MAX_POSTS_PER_SOURCE = 10
    
    def __init__(self):
        super().__init__()
    
    def run(self):
        super().run()

        # Preamble logging.
        print('Beginning the automation script for updating data: Renungan YKB')
        
        # Get all the list of source lists.
        src_list = self.json_data['data']['ykb']

        # The legacy list.
        src_list_old = deepcopy(src_list)

        for i in range(len(src_list)):
            current_src = src_list[i]['url']
            current_node = src_list[i]['posts']

            print(f'[{self.__class__.__name__}] Scraping today\'s devotional from the source: {current_src}')
            
            # Retrieve the YKB page content and its metadata.
            a = self.scrape_page(current_src)

            # Check if this newly retrieved data has previously been scraped.
            previous_data = src_list_old[i]['posts']
            data_exists = False
            for j in range(len(previous_data)):
                if a['date'] == previous_data[j]['date']:
                    print(f'[{self.__class__.__name__}] Already scraped for the title: {a["title"]} ({a['date']})')
                    data_exists = True
                    break

            if not data_exists:
                # Applying changes.
                print(f'[{self.__class__.__name__}] Prepending the following post to node: {a["title"]} ({a['date']})')
                current_node.insert(0, a)
        
            # Ensuring that there are at most N-number of posts in each source list.
            print(f'[{self.__class__.__name__}] Pruning the dictionary ...')
            for b in current_node[self.MAX_POSTS_PER_SOURCE:]:
                current_node.remove(b)
        
        # Write changes.
        super().write(write_msg='ykb')

        # Finalizing the script.
        super().finish()

    def scrape_page(self, url: str):
        """ :return: The cleaned HTML string of the scraped target HTML page. """

        # Retrieve the YKB page.
        r = self.rq.get(url)
        c = html.fromstring(r.content)

        # Building the post content dictionary.
        a = {}

        # The scraped devotional title.
        a['title'] = [l.strip() for l in c.xpath('//div[@class="col-md-9 col-sm-9 col-xs-8 title-renungan"]/h4/text()')][0].title()
        
        # The scraped shortlink of the page.
        a['shortlink'] = [l.strip() for l in c.xpath('//link[@rel="shortlink"]/@href')][0]

        # The scraped year.
        _y = \
        [l.strip() for l in c.xpath('//table[@class="wp-calendar multiple-ajax-calendar-2"]/caption/text()')][0].split(
            ' ')[1]

        # The scraped devotional scripture.
        _scripture = c.xpath('//p[@class="has-text-align-center"]//text()[normalize-space()]')
        a['scripture'] = '' if len(_scripture) == 0 else _scripture

        # The scraped month.
        _m = [l.strip() for l in c.xpath('//div[@class="devotion-date-bulan"]/span/text()')][0]
        _m = months_map[_m.lower()]
        _m = zero_pad(_m)

        # The scraped day.
        _d = [l.strip() for l in c.xpath('//span[@class="devotion-date-tgl"]/text()')][0]
        _d = zero_pad(_d)

        # Build the date.
        a['date'] = f'{_y}-{_m}-{_d}'

        # The scraped featured image.
        _img = c.xpath('//div[@class="renungan-padding content-devotion main-audio-xs"]//figure//img/@src')

        # The main HTML content
        _html = c.xpath('//div[@class="renungan-padding content-devotion main-audio-xs"]')[0]

        # Removing bloated and unecessary image attributes.
        # Only do if the page has a featured image.
        if len(_img) > 0:
            a['featured-image'] = _img[0]

            # Prepending with the cleansed image tag.
            new_img = html.Element('img', src=_img[0])

            # Replacing the scraped HTML content's (bloated) image tag with the cleansed one.
            xx = _html.getparent().xpath('.//figure')[0]
            yy = _html.getparent().xpath('.//figure')[0].xpath('.//figure')[0]
            zz = _html.getparent().xpath('.//figure')[0].xpath('.//figure')[0].xpath('.//img')[0]
            yy.remove(zz)
            xx.remove(yy)

            # Then place the new, cleansed image.
            xx.insert(0, new_img)

        else:
            a['featured-image'] = ''

        # ----- HTML CLEANSING ----- #
        # Wrap the scraped image around a container (and of course body tag!)
        tag_html = html.Element('html')
        tag_head = html.Element('head')
        tag_css = html.Element('style')
        tag_body = html.Element('body')
        tag_container = html.Element('div')

        tag_html.insert(0, tag_head)
        tag_html.insert(1, tag_body)
        tag_head.insert(0, tag_css)
        tag_body.insert(0, tag_container)

        tag_container.set('class', 'main-container')
        tag_container.insert(0, _html)

        # Append title
        tag_title = html.Element('h2')
        tag_title.text = a['title']
        tag_container.insert(0, tag_title)

        # Append date
        tag_date = html.Element('div')
        tag_date.set('class', 'date')
        tag_date.text = f'{str(int(_d))} {months_indonesian[int(_m) - 1]} {_y}'
        tag_container.insert(1, tag_date)

        with open('v2/static/stylesheet_ykb.css', 'r') as fi:
            tag_css.text = fi.read()

        # The export HTML content.
        c_export = deepcopy(tag_html)

        # Prettifying the export.
        c_export = html.tostring(c_export, method='html', encoding='utf-8').decode('utf-8')
        c_export = c_export.replace('<em> </em>', '').replace('<p> </p>', '')

        # Cleaning redundant newline characters and prettifying.
        while True:
            if c_export.__contains__('\n\n'):
                c_export = c_export.replace('\n\n', '')
            else:
                break

        # Whitespace cleaning.
        while True:
            if c_export.__contains__('  '):
                c_export = c_export.replace('  ', ' ')
            else:
                break

        # Tab stripping.
        while True:
            if c_export.__contains__('\t'):
                c_export = c_export.replace('\t', ' ')
            else:
                break

        # Applying and saving the content.
        a['html'] = c_export.strip()

        # Returning the data.
        return a


if __name__ == "__main__":
    scraper = ScraperYKB()
    scraper.run()
