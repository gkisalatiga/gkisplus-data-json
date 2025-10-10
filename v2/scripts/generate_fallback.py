import json
import os


class FallbackGenerator():
    
    # The list of paths to all JSON files.
    JSON_PATH_LIST = [
        'v2/data/gkisplus-gallery.json',
        'v2/data/gkisplus-main.json',
        'v2/data/gkisplus-modules.json',
        'v2/data/gkisplus-static.json',
    ]
    
    def __init__(self):
        pass
    
    def run(self):
        for l in self.JSON_PATH_LIST:
            print(f'[{self.__class__.__name__}] Generating the JSON fallback file for path: {l} ...')
            self.generate_fallback(l)

    def generate_fallback(self, path: str):
        """ Generate a fallback file for a given JSON file provided by "path".. """
        
        # Opening the JSON file.
        with open(path, 'r') as fi:
            j = json.load(fi)
        
        # Updating metadata.
        j['meta']['update-count'] = 1
        j['meta']['last-update'] = 1
        j['meta']['last-updated-item'] = '.'
        j['meta']['last-actor'] = 'FALLBACK'
        
        if path.__contains__('gallery'):
            for i in range(len(j['gallery']) - 1):
                j['gallery'].pop(0)
            for i in range(len(j['gallery'][0]['album-data']) - 1):
                j['gallery'][0]['album-data'].pop(0)
            for i in range(len(j['gallery'][0]['album-data'][0]['photos']) - 1):
                j['gallery'][0]['album-data'][0]['photos'].pop(0)
        
        elif path.__contains__('main'):
            # Shrinking YouTube list.
            for i in range(len(j['data']['yt']) - 1):
                j['data']['yt'].pop(0)
            for i in range(len(j['data']['yt'][0]['content']) - 1):
                j['data']['yt'][0]['content'].pop(0)
            # Shrinking PDF warta and liturgi.
            for i in range(len(j['data']['pdf']['wj']) - 1):
                j['data']['pdf']['wj'].pop(0)
            for i in range(len(j['data']['pdf']['liturgi']) - 1):
                j['data']['pdf']['liturgi'].pop(0)
            for i in range(len(j['data']['pdf']['es']) - 1):
                j['data']['pdf']['es'].pop(0)
            # Shrinking agenda.
            for l in j['data']['agenda'].keys():
                for i in range(len(j['data']['agenda'][l]) - 1):
                    j['data']['agenda'][l].pop(0)
            # Shrinking forms.
            for i in range(len(j['data']['forms']) - 3):
                j['data']['forms'].pop(0)
            # Shrinking YKB.
            for a in j['data']['ykb']:
                for i in range(len(a['posts']) - 1):
                    a['posts'].pop(0)
            # Shrinking offertory code.
            for i in range(len(j['data']['offertory-code']) - 3):
                j['data']['offertory-code'].pop(0)
            # Shrinking carousel.
            for i in range(len(j['data']['carousel']) - 2):
                j['data']['carousel'].pop(0)
            # Shrinking pukat berkat.
            for i in range(len(j['data']['pukat-berkat']) - 1):
                j['data']['pukat-berkat'].pop(0)
            # Shrinking agenda ruangan.
            for i in range(len(j['data']['agenda-ruangan']) - 1):
                j['data']['agenda-ruangan'].pop(0)
            # Messing around with the flags.
            j['data']['backend']['is_easter_egg_devmode_enabled'] = 0
            j['data']['backend']['is_feature_agenda_shown'] = 0
            j['data']['backend']['is_feature_bible_shown'] = 0
            j['data']['backend']['is_feature_esliturgy_shown'] = 0
            j['data']['backend']['is_feature_formulir_shown'] = 0
            j['data']['backend']['is_feature_galeri_shown'] = 0
            j['data']['backend']['is_feature_lapak_shown'] = 0
            j['data']['backend']['is_feature_library_shown'] = 0
            j['data']['backend']['is_feature_persembahan_shown'] = 0
            j['data']['backend']['is_feature_seasonal_shown'] = 0
            j['data']['backend']['is_feature_ykb_shown'] = 0
        
        elif path.__contains__('modules'):
            for i in range(len(j['modules']['bible']) - 1):
                j['modules']['bible'].pop(0)
            for i in range(len(j['modules']['library']) - 1):
                j['modules']['library'].pop(0)
        
        elif path.__contains__('static'):
            for i in range(len(j['static']) - 1):
                j['static'].pop(0)
            for i in range(len(j['static'][0]['content']) - 1):
                j['static'][0]['content'].pop(0)
        
        # Preparing the save file string.
        k = os.path.split(path)
        save_filename = k[1].replace('gkisplus-', 'fallback_')
        save_filepath = os.path.join(k[0], save_filename)
        
        # Write the compactified JSON file.
        with open(save_filepath, 'w') as fo:
            json.dump(j, fo, separators=(',', ':'))
        
        del j

if __name__ == "__main__":
    generator = FallbackGenerator()
    
    generator.run()
    print('The fallback version of the JSON files has been generated successfully!')
