import pypyodbc
import re

### This function parses a title in the IMDB Database
def parsetitle(title):
    localTitle = title
    finalTitle = ''
    titleType = "Movie"
    titleEpisode = ""

    # Look for different title formats
    # Made for Video, Made for TV, Video Game, TV or Movie (default)
    if title.find('(V)') >= 0:
        titleType = "Made for Video"
        localTitle = localTitle.replace(' (V)', '')
    if title.find('(TV)') >= 0:
        titleType = "Made for TV"
        localTitle = localTitle.replace(' (TV)', '')
    if title.find('(VG)') >= 0:
        titleType = "Video Game"
        localTitle = localTitle.replace(' (VG)', '')
    if title.count('"') >= 2:
        titleType = "TV"
        localTitle = localTitle.replace('"', '')

    # Now look for the year and any duplicate value
    # For Movie/Show duplicates, the year will be followed by /<Roman Numeral>
    found = re.search('\([0-9?]{4,4}[/IV]{0,4}\)',title)
    year = ''
    dupVal = '0'
    yearIndex = -1
    if not(found == None):
        tmpYear = found.group(0)
        yearIndex = title.find(tmpYear) # Store the Index so other searches can start here
        if tmpYear.find('/') > 0:
            # This is a duplicate, store that too
            year = re.search('[0-9?]{4,4}', tmpYear).group(0)
            dupVal = tmpYear[tmpYear.find('/')+1:].replace(')','')
        else:
            # No duplicate, just grab the year
            year = tmpYear.replace('(','').replace(')','')
            dupVal = '0'
        localTitle = localTitle.replace(tmpYear,'')
    else:
        # Every Title should have a year, this isn't good
        # Should throw an error or something
        year = '0'
        dupVal = '0'

    # the title of the movie is the text prior to the year
    finalTitle = title[0:yearIndex].strip()

    # See if there is an episode title/info
    # INCOMPLETE
    # This is hacked together.  We find the first { and last } and grab everything in between
    epIndex = title.find('{')
    if epIndex >= 0:
        # Get the Episode Title information
        # Everything between the {}
        titleEpisode = title[title.find('{'):title.find('}')+1]
        localTitle = localTitle.replace(titleEpisode,'')
        titleEpisode = titleEpisode.replace('{','').replace('}','')

    # Look for an alias (as XXX)
    # Anything in () that starts with "as "
    alias = ''
    found = re.search('\(as (.*?)\)',title.replace(titleEpisode,'')[yearIndex+2:])
    if not(found == None):
        alias = found.group(0).replace('(as ', '').replace(')', '')
        localTitle = localTitle.replace(found.group(0),'')

    # See if any role is uncredited
    uncredited = 0
    if localTitle.find('(uncredited)') > 0:
        uncredited = 1
        localTitle.replace('(uncredited)', '')


    # Check for an order
    # This is mainly for actors and actresses, order displayed in IMDB
    # A number within <>
    orderVal = '0'
    if yearIndex > 0:
        found = re.search('<(.*?)>', title[yearIndex + 2:])
        if not (found == None):
            orderVal = found.group(0).replace('<', '').replace('>', '')
            localTitle = localTitle.replace(found.group(0), '')

    # Check for a role
    # This is for actors/actresses and is the role played
    # Anything between []
    role = ''
    if yearIndex > 0:
        found = re.search('\[(.*?)\]', title[yearIndex + 2:])
        if not (found == None):
            role = found.group(0).replace('[', '').replace(']', '')
            localTitle = localTitle.replace(found.group(0), '')

    # Remove any remaining () items still in the title
    # This is where localTitle comes in, since we've been cleansing it
    # These are typically the specific jobs for crew
    # Put them in the returned dict as 'other'
    otherItem = ''
    if yearIndex > 0:
        found = re.search('\((.*?)\)',localTitle)
        if not(found == None):
            otherItem = found.group(0).replace('(','').replace(')','')
            localTitle = localTitle.replace(found.group(0),'')

    # Return a named array of the values we found
    returnArray = {'title':finalTitle.strip(),'year':year,'dup':dupVal,'episode':titleEpisode,'type':titleType,'other':otherItem,'order':orderVal,'role':role,'uncredited':uncredited,'alias':alias}
    return returnArray

### This function will save many titles to the MySQL database
def saveTitle_Batch(titledict):
    # Connect to the Database
    conn = pypyodbc.connect('DSN=moviesmysql')
    cur = conn.cursor()

    # print("Save Time")
    query = 'insert into movies.imdb_title (id, title, year, type, episode_full, primary_language, dup) values '
    lastKey = ''
    for row in titledict:
        if not(lastKey == row['key']):
            query += " ('" + str(row['id']) + "', '"+ row['title'].replace("'","''").replace('\\','\\\\') + "', '" + str(row['year']).replace('????','0') + "', '" + row['type'] + "', '" + row['episode'].replace("'", "''").replace('\\', '\\\\') + "', '" + row['language'] + "', '" + row['dup'] + "'),"
            lastKey = row['key']

    # print(query[0:len(query)-1])
    # remove last ,
    query = query[0:len(query)-1]

    #print(query)

    # Save to the database
    cur.execute(query)
    cur.commit()

    # Close the database connection
    conn.close()

### This function will save many titles to the MySQL database
def savePerson_Batch(directorDict):
    # Connect to the Database
    conn = pypyodbc.connect('DSN=moviesmysql')
    cur = conn.cursor()

    # print("Save Time")
    query = 'insert into movies.imdb_title_person (title_id, person_source, person_type, name, dup, role, order_val, alias, uncredited) values '
    lastKey = ''
    for row in directorDict:
        # if not(lastKey == row['key']):
        query += " ('" + str(row['id']) + "', '"+ row['source'] + "', '" + row['person_type'].replace("'","''") + "', '" + str(row['name']).replace("'", "''") + "', '" + row['dup_p'] + "', '" + str(row['role_p']).replace("'", "''") + "', '" + str(row['order_p']) + "', '" + row['alias_p'].replace("'","''") + "', '" + str(row['uncredited_p']) + "'),"
        lastKey = row['key']

    # print(query[0:len(query)-1])
    # remove last ,
    query = query[0:len(query)-1]

    #print(query)

    # Save to the database
    cur.execute(query)
    cur.commit()

    # Close the database connection
    conn.close()

### This function will save many titles to the MySQL database
def saveGenres(genreDict):
    # Connect to the Database
    conn = pypyodbc.connect('DSN=moviesmysql')
    cur = conn.cursor()

    # print("Save Time")
    query = 'insert into movies.imdb_title_genre (title_id, line, genre) values '
    lastKey = ''
    for row in genreDict:
        # if not(lastKey == row['key']):
        query += " ('" + str(row['id']) + "', '" + str(row['line']) + "', '" + row['genre'] + "'),"
        lastKey = row['key']

    # print(query[0:len(query)-1])
    # remove last ,
    query = query[0:len(query)-1]

    #print(query)

    # Save to the database
    cur.execute(query)
    cur.commit()

    # Close the database connection
    conn.close()
