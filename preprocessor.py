import re
import os
import shutil

PATH_OUTPUT = "docs"
PATH_LYRICS = "lyrics"

YAML_SEPARATOR = "---\n"
YAML_KEY_VALUE = "{0: <16}: {1}\n"

HTML_SECTION = '<div class="lyrics">\n{}\n</div>\n'
HTML_SECTION_TYPE = '<div class="lyrics-type">{}<hr></div>\n'
HTML_SECTION_TITLE = '<h2>{}</h2>\n'
HTML_SECTION_CONTENT = '<p>\n{}\n</p>'

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

def process_content(content):
    return content.strip().replace("\n", "<br>\n")

class LyricsFile:
    def __init__(self, file_name, artist_id):
        self.file_name = file_name
        # self.song_id = ""
        self.artist_ids = [artist_id]

        self.lang = ""
        self.section_titles = []
        self.section_texts = []

    def _parse_header(self, header):
        for match in re.finditer(r"([a-zA-Z\-_]+):\s+([a-zA-Z\-_]+)", header):
            key, value = match.groups()

            if key == "lang":
                self.lang = value
            elif key == "feat":
                self.artist_ids.extend(value.split(","))
    
    def _parse_contents(self, contents):
        for match in re.finditer(r"-{3,}\[(.+)\]-{3,}\s*([\s\S]+?)(?=-{3,}\[(?:.+)\]-|$)", contents):
            title, text = match.groups()
            self.section_titles.append(title)
            self.section_texts.append(text)
    
    def parse(self, text):
        # parse name
        # self.song_id = re.match(r"(?:\d+-){3}(.+)\.", self.file_name).group(1)

        header, contents = re.match(r"^((?:[a-zA-Z\-_]+:\s+[a-zA-Z\-_]+\n)+)\n([\s\S]+)", text).groups()
        self._parse_header(header)
        self._parse_contents(contents)
        return self

    def generate(self):
        artist_folder, posts_folder = make_artist(self.artist_ids[0])

        for artist_id in self.artist_ids[1:]:
            make_artist(artist_id)

        file_name = os.path.splitext(self.file_name)[0]

        with open(os.path.join(posts_folder, file_name + ".html"), "w") as fh:
            fh.write(YAML_SEPARATOR)
            fh.write(YAML_KEY_VALUE.format("layout", "post"))
            fh.write(YAML_KEY_VALUE.format("title", '"' + "・".join(self.section_titles) + '"'))
            fh.write(YAML_KEY_VALUE.format("artist_ids", str(self.artist_ids)))
            fh.write(YAML_SEPARATOR)
            fh.write("\n")

            num_sections = len(self.section_texts)
            for section_no in range(num_sections):
                section_inner = ""
                section_inner += HTML_SECTION_TYPE.format(lang_config[self.lang]["sections"][section_no])
                section_inner += HTML_SECTION_TITLE.format(self.section_titles[section_no])

                section_inner += HTML_SECTION_CONTENT.format(process_content(self.section_texts[section_no]))

                fh.write(HTML_SECTION.format(section_inner))

                if section_no < num_sections - 1:
                    fh.write("\n")


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
                LyricsFile(lyrics_file_name, artist_id)\
                    .parse(fh.read())\
                    .generate()
