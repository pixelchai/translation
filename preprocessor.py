import re
import os
import shutil

PATH_OUTPUT = "docs"
PATH_LYRICS = "lyrics"

YAML_SEPARATOR = "---\n"
YAML_KEY_VALUE = "{0: <16}: {1}\n"

HTML_LYRICS = '<div class="lyrics">\n{}</div>\n'
HTML_SECTION = '<div class="lyrics-section">\n{}</div>\n'
HTML_SECTION_PART = '<p class="lyrics-{}">\n{}\n</p>\n'

lyrics_id_names = {
    1: ["translation"],
    2: ["transcription", "translation"],
    3: ["transcription", "transliteration", "translation"],
}

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
        self.artist_ids = [artist_id]

        self.lang = ""
        self.titles = []
        self.sections = []

        self.post = ""

    def _parse_header(self, header):
        for match in re.finditer(r"([a-zA-Z\-_]+):\s+([a-zA-Z\-_]+)", header):
            key, value = match.groups()
            value_split = [x.strip().replace(";com", ",") for x in value.split(",")]

            if key == "lang":
                self.lang = value
            elif key == "feat":
                self.artist_ids.extend(value_split)
            elif key == "title":
                self.titles.extend(value_split)

    def _parse_contents(self, contents):
        for match in re.finditer(r"([\s\S]*?)(?:^\/\/\s*$|$(?![\r\n]))", contents, re.M):
            section = match.group(1).strip()

            if len(section) > 0:
                parts = [x.strip() for x in re.split(r"\n{2,}", section)]
                self.sections.append(parts)
    
    def parse(self, text):
        header, post, contents = [x.group(1) for x in re.finditer(r"([\s\S]*?)(?:^\/\/-{3,}$|$(?![\r\n]))", text, re.M)][:3]
        self.post = post.strip()
        self._parse_header(header)
        self._parse_contents(contents)
        return self

    def generate(self):
        artist_folder, posts_folder = make_artist(self.artist_ids[0])

        for artist_id in self.artist_ids[1:]:
            make_artist(artist_id)

        file_name = os.path.splitext(self.file_name)[0]

        with open(os.path.join(posts_folder, file_name + ".md"), "w") as fh:
            fh.write(YAML_SEPARATOR)
            fh.write(YAML_KEY_VALUE.format("layout", "post"))
            fh.write(YAML_KEY_VALUE.format("title", '"' + "・".join(self.titles) + '"'))
            fh.write(YAML_KEY_VALUE.format("artist_ids", str(self.artist_ids)))
            fh.write(YAML_SEPARATOR)
            fh.write("\n")

            fh.write(self.post)
            fh.write("\n\n")

            lyrics_inner = ""
            for section in self.sections:
                section_inner = ""

                id_names = lyrics_id_names[len(section)]
                for part_no, part in enumerate(section):
                    section_inner += HTML_SECTION_PART.format(id_names[part_no], part)

                lyrics_inner += HTML_SECTION.format(section_inner)
            
            fh.write(HTML_LYRICS.format(lyrics_inner))


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
