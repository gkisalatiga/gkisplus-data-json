import json
import os


class Minify():
    
    # The list of paths to all JSON files.
    JSON_PATH_LIST = [
        'staging/data/feeds.json',
        'staging/data/gkisplus-gallery.json',
        'staging/data/gkisplus-main.json',
        'staging/data/gkisplus-modules.json',
        'staging/data/gkisplus-static.json',
    ]
    
    def __init__(self):
        pass
    
    def run(self):
        for l in self.JSON_PATH_LIST:
            print(f'[{self.__class__.__name__}] Minifying the JSON path: {l} ...')
            self.minify_json(l)

    def minify_json(self, path: str):
        """ Minify a given JSON file provided by "path". """
        
        # Opening the JSON file.
        with open(path, 'r') as fi:
            j = json.load(fi)
        
        # Preparing the save file string.
        k = os.path.split(path)
        save_filename = k[1].replace('.json', '.min.json')
        save_filepath = os.path.join(k[0], save_filename)
        
        # Write the compactified JSON file.
        with open(save_filepath, 'w') as fo:
            json.dump(j, fo, separators=(',', ':'))


if __name__ == "__main__":
    minifier = Minify()
    
    minifier.run()
    print('JSON files are validated and minifed!')
