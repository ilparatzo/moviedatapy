from imdb import imdb_helper
import pandas
import re


# Function to load all titles from a movie file
# Returns a pandas dataframe
def load_titles(type_to_find, file_to_load, id_start):
    movies = open(file_to_load, "rt", encoding="utf-8")

    # state is 0, waiting, until we find "MOVIES LIST"
    state = 0
    full_list = []
    curr_id = id_start
    for line in movies:
        if state == 0:
            # We're waiting for the right header
            if line.find("MOVIES LIST") >= 0:
                state = 1
        elif state == 1:
            # We're reading movies
            # skip ='s and empties and -'s
            if not(line[0:2] == "==" or line[0:2] == "--" or len(line) <= 3):
                # Grab the title, everything prior to the first tab
                main_title = line[0:line.find('\t')]
                main_title = main_title.replace('{{SUSPENDED}}', '{SUSPENDED}')

                # Parse the title for all the pieces we need
                title_data = imdb_helper.parse_title(main_title)
                if title_data['type'] == type_to_find and len(title_data['title']) > 0:
                    # INCOMPLETE
                    # This ID is only valid during this one run
                    curr_id += 1
                    title_data['id'] = curr_id
                    # titleData['key'] = titleData['title'] + "|" + titleData['year'] + "|" + titleData['dup']

                    # This came back with a bunch of stuff we don't need
                    # Drop unneeded columns
                    title_data.pop('order', None)
                    title_data.pop('role', None)
                    title_data.pop('uncredited', None)
                    title_data.pop('alias', None)

                    # save it
                    full_list.append(title_data)

    return pandas.DataFrame(full_list)


# Function to load languages
# Returns a pandas dataframe
def load_languages(type_to_find, file_to_load, single_lang):
    # START HERE
    movies = open(file_to_load, "rt", encoding="utf-8")

    # state is 0, waiting, until we find "LANGUAGE LIST"
    state = 0
    full_list = []
    last_movie = ''
    for line in movies:
        if state == 0:
            # We're waiting for the right header
            if line.find("LANGUAGE LIST") >= 0:
                state = 1
        elif state == 1:
            # We're reading movies
            # skip ='s and empties
            if not(line[0:2] == "==" or len(line) <= 3):
                # Grab the title, everything prior to the first tab
                main_title = line[0:line.find('\t')]
                title_data = imdb_helper.parse_title(main_title)

                # Make sure it's the type we care about
                if title_data['type'] == type_to_find:
                    # Grab everything after the first tab
                    lang_search = line[line.find('\t'):]
                    # Trim tabs at the front
                    lang_search = lang_search.lstrip(' \t')
                    # Find everything that is a character or space at the front
                    found = re.search('^([A-Za-z ]*)', lang_search)
                    language = ''
                    if found is not None:
                        language = found.group(0)

                    # Save it!  We only use the first listed language
                    if len(language) > 0 and (single_lang == 0 or last_movie != title_data['key']):
                        title_data['language'] = language

                        # create an object with the movie's key and the language
                        tmp_data = {'key': title_data['key'], 'primary_language': language}
                        full_list.append(tmp_data)
                        last_movie = title_data['key']

    return pandas.DataFrame(full_list)


# Function to load Genres
# Returns a pandas dataframe
def load_genres(type_to_find, file_to_load, single_genre):
    # START HERE
    movies = open(file_to_load, "rt", encoding="utf8")

    # state is 0, waiting, until we find "LANGUAGE LIST"
    state = 0
    full_list = []
    last_movie = ''
    line_val = 0
    for line in movies:
        if state == 0:
            # We're waiting for the right header
            if line.find("THE GENRES LIST") >= 0:
                state = 1
        elif state == 1:
            # We're reading movies
            # skip ='s, -'s and empties
            if not(line[0:2] == "==" or line[0:2] == '--' or len(line) <= 3):
                # Grab the title, everything prior to the first tab
                main_title = line[0:line.find('\t')]
                title_data = imdb_helper.parse_title(main_title)

                # New movie?
                if last_movie != title_data['key']:
                    line_val = 1
                else:
                    line_val += 1

                # Make sure it's the type we care about
                if title_data['type'] == type_to_find:
                    # Grab everything after the first tab
                    genre_search = line[line.find('\t'):]
                    # Trim tabs at the front
                    genre_search = genre_search.lstrip(' \t')
                    # Find everything that is a character or space at the front
                    found = re.search('^([A-Za-z -]*)', genre_search)
                    genre = ''
                    if found is not None:
                        genre = found.group(0)

                    if len(genre) > 0 and (single_genre == 0 or last_movie != title_data['key']):
                        title_data['genre'] = genre
                        tmp_data = {'key': title_data['key'], 'genre': genre, 'line': line_val}
                        full_list.append(tmp_data)
                        last_movie = title_data['key']

    return pandas.DataFrame(full_list)


# Function to load one of any of the people/person related files
# Validated against: actors, actresses, directors, producers, miscellaneous
# Returns a pandas dataframe
def load_persons(type_to_find, file_to_load, default_person_type, person_source):
    # START HERE
    movies = open(file_to_load, "rt", encoding="utf8")

    # state is 0, waiting, until we find "Name\t"
    state = 0
    full_list = []
    last_person = ''
    for line in movies:
        if state == 0:
            # We're waiting for the right header
            if line.find("Name\t") >= 0 or line.find("Name ") >= 0:
                state = 1
        elif state == 1:
            # We're reading movies
            # skip ='s and empties
            if not (line[0:2] == "--" or len(line) <= 3):
                # Get producer name, everything prior to the first tab
                if line[0:1] == '\t':
                    person = last_person
                else:
                    person = line[0:line.find('\t')]
                    last_person = person

                # Title, all text after last tab
                main_title = line[line.rfind('\t') + 1:]
                title_data = imdb_helper.parse_title(main_title)

                # Type of person listed?
                person_type = default_person_type
                if len(title_data['other']) > 0:
                    person_type = title_data['other'].replace('(', '').replace(')', '')

                # Role (if actor or actress)
                role = ''
                if len(title_data['role']) > 0:
                    role = title_data['role']

                order_val = ''
                if len(title_data['order']) > 0:
                    order_val = title_data['order']

                uncredited = 0
                if title_data['uncredited'] >= 0:
                    uncredited = title_data['uncredited']

                alias = ''
                if len(title_data['alias']) > 0:
                    alias = title_data['alias']

                # Dup name?
                found = re.search('\([IVX]{1,4}\)', person)
                dup_val = '0'
                if not (found is None):
                    dup_val = found.group(0).replace('(', '').replace(')', '')
                    person = person.replace(found.group(0), '')

                # Make sure it's the type we care about
                if title_data['type'] == type_to_find:
                    tmp_data = {'key': title_data['key'], 'person_source': person_source,
                                'person_type': person_type, 'name': person, 'dup': dup_val,
                                'role': role, 'order_val': order_val,
                                'alias': alias, 'uncredited': uncredited}
                    full_list.append(tmp_data)

    return pandas.DataFrame(full_list)
