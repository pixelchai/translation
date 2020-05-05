import re
import os
import shutil

PATH_OUTPUT = "docs"
PATH_LYRICS = "lyrics"

YAML_SEPARATOR = "---\n"
YAML_KEY_VALUE = "{0: <16}: {1}\n"

lang_config = {
    "jp": {
        "sections": ["Kanji", "Roumaji", "English"]
    }
}

def make_artist(artist_id):
    artist_folder = os.path.join(PATH_OUTPUT, PATH_LYRICS, artist_id)
    posts_folder = os.path.join(artist_folder, "_posts")

    try:
        os.makedirs(posts_folder)

        with open(os.path.join(artist_folder, "index.html"), "w") as fh:
            fh.write(YAML_SEPARATOR)
            fh.write(YAML_KEY_VALUE.format("layout", "artist"))
            fh.write(YAML_KEY_VALUE.format("artist_id", artist_id))
            fh.write(YAML_SEPARATOR)
    except:
        pass
    
    return artist_folder, posts_folder

class LyricsFile:
    def __init__(self, artist_id, song_id):
        self.song_id = song_id
        self.artist_ids = [artist_id]

        self.lang = ""
        self.sections = []
    
    def parse(self, fh):
        print(self.artist_ids)
        return self

    def generate(self):
        for artist_id in self.artist_ids:
            make_artist(artist_id)

if __name__ == "__main__":
    # delete previously generated output
    path_out_lyrics = os.path.join(PATH_OUTPUT, PATH_LYRICS)
    if os.path.isdir(path_out_lyrics):
        shutil.rmtree(path_out_lyrics)

    # copy artist.yml file
    shutil.copy2(os.path.join(PATH_LYRICS, "artists.yml"),
                 os.path.join(PATH_OUTPUT, "_data"))
    
    # preprocess lyrics files
    for artist_id in os.listdir(PATH_LYRICS):
        artist_dir = os.path.join(PATH_LYRICS, artist_id)
        if not os.path.isdir(artist_dir): continue

        for lyrics_file_name in os.listdir(artist_dir):
            name = re.match(r"(?:\d+-){3}(.+)\.", lyrics_file_name).group(1)
            
            with open(os.path.join(artist_dir, lyrics_file_name)) as fh:
                LyricsFile(artist_id, name).parse(fh).generate()
