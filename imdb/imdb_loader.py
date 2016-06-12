from imdb import imdb_helper
import pandas
import re

# A list of languages that will be recognized in the Language processor
languageList = ['Arabic','Bulgarian','Chinese','Croatian','Dutch','English','Finnish','French','German','Greek','Hebrew','Hindi','Hungarian','Icelandic','Italian','Japanese','Korean','Norwegian','Persian','Polish','Portuguese','Punjabi','Romanian','Russian','Spanish','Swedish','Turkish','Ukrainian','Mandarin','Cantonese']


# Function to load all titles from a movie file
# Returns a pandas dataframe
def load_titles(typeToFind, fileToLoad, idStart):
    movies = open(fileToLoad, "rt", encoding="utf-8")

    # state is 0, waiting, until we find "MOVIES LIST"
    state = 0
    fullList = []
    id = idStart
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
                mainTitle = line[0:line.find('\t')]
                mainTitle = mainTitle.replace('{{SUSPENDED}}','{SUSPENDED}')

                # Parse the title for all the pieces we need
                titleData = imdb_helper.parsetitle(mainTitle)
                if titleData['type'] == typeToFind and len(titleData['title']) > 0:
                    # INCOMPLETE
                    # This ID is only valid during this one run
                    id += 1
                    titleData['id'] = id
                    #titleData['key'] = titleData['title'] + "|" + titleData['year'] + "|" + titleData['dup']

                    # This came back with a bunch of stuff we don't need
                    # Drop unneeded columns
                    titleData.pop('order', None)
                    titleData.pop('role', None)
                    titleData.pop('uncredited', None)
                    titleData.pop('alias', None)

                    # save it
                    fullList.append(titleData)
    return pandas.DataFrame(fullList)

# Function to load languages
# Returns a pandas dataframe
def findLanguages(typeToFind, fileToLoad, singleLang):
    # START HERE
    movies = open(fileToLoad, "rt", encoding="utf-8")

    # state is 0, waiting, until we find "LANGUAGE LIST"
    state = 0
    counter = 0
    fullList = []
    lastMovie = ''
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
                mainTitle = line[0:line.find('\t')]
                titleData = imdb_helper.parsetitle(mainTitle)

                # Make sure it's the type we care about
                if titleData['type'] == typeToFind:
                    # We just look for the languages we're interested in
                    langSearch = line[line.find('\t'):]
                    language = ''
                    for lang in languageList:
                        if langSearch.find(lang) >= 0:
                            language = lang
                            break;
                    if len(language) > 0 and (singleLang == 0 or lastMovie != titleData['title'] + "|" + titleData['year']):
                        #movieList[movieList.key == titleData['title'] + "|" + titleData['year']]['language'] = language
                        titleData['language'] = language
                        tmpData = {'key':titleData['key'], 'language':language}
                        fullList.append(tmpData)
                        #print(language)
                        lastMovie = titleData['title'] + "|" + titleData['year']


    return pandas.DataFrame(fullList)

# Function to load Genres
# Returns a pandas dataframe
def loadGenres(typeToFind, fileToLoad, singleGenre):
    # START HERE
    movies = open(fileToLoad, "rt", encoding="utf8")

    # state is 0, waiting, until we find "LANGUAGE LIST"
    state = 0
    counter = 0
    fullList = []
    lastMovie = ''
    lineVal = 0
    for line in movies:
        if state == 0:
            # We're waiting for the right header
            if line.find("THE GENRES LIST") >= 0:
                state = 1
        elif state == 1:
            # We're reading movies
            # skip ='s and empties
            if not(line[0:2] == "==" or len(line) <= 3):
                # Grab the title, everything prior to the first tab
                mainTitle = line[0:line.find('\t')]
                titleData = imdb_helper.parsetitle(mainTitle)

                # New movie?
                if lastMovie != titleData['key']:
                    lineVal = 1
                else:
                    lineVal += 1

                # Make sure it's the type we care about
                if titleData['type'] == typeToFind:
                    # Pull the Genre on this line
                    genre = line[line.rfind('\t'):]
                    if len(genre) > 0 and (singleGenre == 0 or lastMovie != titleData['title'] + "|" + titleData['year'] + "|" + titleData['dup']):
                        titleData['genre'] = genre
                        tmpData = {'key':titleData['key'], 'genre':genre, 'line':lineVal}
                        fullList.append(tmpData)
                        #print(language)
                        lastMovie = titleData['key']

    return pandas.DataFrame(fullList)

# Function to load one of any of the people/person related files
# Validated against: actors, actresses, directors, producers, miscellaneous
# Returns a pandas dataframe
def loadPerson(typeToFind, fileToLoad, defaultPersonType, personSource):
    # START HERE
    movies = open(fileToLoad, "rt", encoding="utf8")

    # state is 0, waiting, until we find "Name\t"
    state = 0
    counter = 0
    fullList = []
    lastPerson = ''
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
                    person = lastPerson
                else:
                    person = line[0:line.find('\t')]
                    lastPerson = person

                # Title, all text after last tab
                mainTitle = line[line.rfind('\t') + 1:]
                titleData = imdb_helper.parsetitle(mainTitle)

                # Type of person listed?
                person_type = defaultPersonType
                if len(titleData['other']) > 0:
                    person_type = titleData['other'].replace('(','').replace(')','')

                # Role (if actor or actress)
                role = ''
                if len(titleData['role']) > 0:
                    role = titleData['role']

                orderVal = ''
                if len(titleData['order']) > 0:
                    orderVal = titleData['order']

                uncredited = 0
                if titleData['uncredited'] >= 0:
                    uncredited = titleData['uncredited']

                alias = ''
                if len(titleData['alias']) > 0:
                    alias = titleData['alias']

                # Dup name?
                found = re.search('\([IVX]{1,4}\)', person)
                dupVal = '0'
                if not (found == None):
                    dupVal = found.group(0).replace('(', '').replace(')', '')
                    person = person.replace(found.group(0), '')

                # Make sure it's the type we care about
                if titleData['type'] == typeToFind:
                    tmpData = {'key': titleData['key'], 'source': personSource,
                               'person_type': person_type, 'name': person, 'dup_p': dupVal, 'role_p':role, 'order_p':orderVal,
                               'alias_p':alias, 'uncredited_p':uncredited}
                    fullList.append(tmpData)

    return pandas.DataFrame(fullList)

