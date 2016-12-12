import pypyodbc
import re
import logging
from datetime import datetime

# Standard RE forms for parsing titles
title_form_1 = '(.+)'
year_form_1 = '[(]([0-9?]{4,4})[/]*([IVXL]{1,6})*[)]'
type_form_1 = '[ ]*(\((V|TV|VG)\))*[ ]*'
episode_form_1 = '[ ]*({(.*)})*[ ]*'
job_form_1 = '[ ]*(\((?!as )(.*?)\))?[ ]*'
alias_form_1 = '[ ]*(\((as )(.*?)\))?[ ]*'
role_form_1 = '[ ]*(\[(.*?)\])?[ ]*'
order_form_1 = '[ ]*(<([0-9]*?)>)?[ ]*'
biz_form_1 = '([A-Z]{3,3})[ ]([0-9,]*)[ ]*([(]([A-Z]+)[)])?[ ]*([(]([0-9A-Za-z ]+)[)])?'

# List of columns for each type of save
column_data = {
    'Movie': ['imdb_title', 'id', 'title', 'year', 'dup', 'type', 'episode_full', 'primary_language'],
    'Genre': ['imdb_title_genre', 'title_id', 'genre', 'line'],
    'Business': ['imdb_title_business', 'title_id', 'biz_type', 'currency', 'country', 'value_date', 'value'],
    'Person': ['imdb_title_person', 'title_id', 'person_source', 'person_type', 'order_val', 'name',
               'dup', 'alias', 'role', 'uncredited']
}


def parse_title(title):
    # Initialize a couple variables
    local_title = title
    title_type = "Movie"

    # Initialize a semi-blank return array
    return_array = {'key': '', 'title': title, 'year': '', 'dup': '',
                    'episode': '', 'type': 'Movie', 'other': '',
                    'order': '', 'role': '', 'uncredited': 0, 'alias': ''}

    # Parse with the title parser
    title_data = re.search(title_form_1 + '[ ]+' + year_form_1 + type_form_1 +
                           episode_form_1 + job_form_1 + alias_form_1 + role_form_1 + order_form_1, local_title)

    # for i in range(0, len(title_data.groups())):
    #     print(str(i) + ":" + title_data.group(i))

    # Did it match?
    if title_data is None:
        # Error, it didn't match
        # return "error"
        logging.error("TITLE PARSE FAILED: " + title)
    else:
        # Parse what we found
        # First, what kind of title is it? (default was movie)
        if title_data.group(5) == "V":
            title_type = "Made for Video"
        elif title_data.group(5) == "TV":
            title_type = "Made for TV"
        elif title_data.group(5) == "VG":
            title_type = "Video Game"
        elif title_data.group(1).count('"') >= 2:
            title_type = "TV"

        # Save the year
        year = title_data.group(2).replace('????', '0')

        # Was there a duplicate value with the year?
        dup_val = title_data.group(3) if title_data.group(3) is not None else ''

        # Title was value 1 (remove any quotes if it was a TV show
        final_title = title_data.group(1).replace('"', '')

        # Episode Information (this is incomplete, needs more parsing)
        title_episode = title_data.group(7) if title_data.group(7) is not None else ''

        # Alias information
        alias = title_data.group(12) if title_data.group(12) is not None else ''

        # Role
        role = title_data.group(14) if title_data.group(14) is not None else ''

        # Order
        order_val = title_data.group(16) if title_data.group(16) is not None else ''

        # Other Item (job typically)
        other_item = title_data.group(9) if title_data.group(9) is not None else ''

        # Uncredited?
        uncredited = 0
        if other_item == "uncredited":
            uncredited = 1

        # assign a key
        # use title|year|dup as a unique title
        title_key = final_title + "|" + year + "|" + dup_val

        # Return a named array of the values we found
        return_array = {'key': title_key, 'title': final_title, 'year': year, 'dup': dup_val,
                        'episode_full': title_episode, 'type': title_type, 'other': other_item,
                        'order': order_val, 'role': role, 'uncredited': uncredited, 'alias': alias}

    return return_array


def create_inserts(data_dict, data_type, file_name):
    # Initialize a file with the requested name
    dbfile = '.sql/tmp/db-inserts_' + str(file_name) + '.sql'
    sqlfile = open(dbfile, 'w', encoding='utf-8')

    # Grab the column list
    my_columns = column_data[data_type]

    # Start building the query
    query = 'insert into movies.' + my_columns[0] + " ("
    for column in my_columns:
        if not(column == my_columns[0]):
            query += column + ", "

    # Remove the last column
    query = query[:-2]
    query += ") values ("

    # Initialize an array of the insert strings
    insert_list = []

    # Run through every row in the data
    for row in data_dict:
        # Initialize the query to what was already built
        my_query = query
        # Run through every column we need to save
        for column in my_columns:
            if not (column == my_columns[0]):
                # accomodate for nulls
                tmp_value = 'null' if len(str(row[column])) == 0 else \
                    "'" + str(row[column]).replace("'", "''").replace('\\', '\\\\') + "'"
                my_query += tmp_value + ", "

        # Remove the last comma and end the parend
        my_query = my_query[:-2]
        my_query += ');' + "\n"

        # Write this out to the file
        insert_list.append(my_query)

    # Write out all the lines
    sqlfile.writelines(insert_list)

    # Close the file
    sqlfile.close()


# Parses business data
def parse_business(biz_string):
    # setup the return dictionary
    return_val = {'currency': '',
                  'value': '',
                  'country': '',
                  'value_date': ''
                  }

    # Run the business form against the string provided
    biz_data = re.search(biz_form_1, biz_string)

    # Did it match?
    if biz_data is None:
        # Error, it didn't match
        # return "error"
        logging.error("BUSINESS PARSE FAILED: " + biz_string)
    else:
        # Parse what we found
        # Currency
        currency = biz_data.group(1)

        # Value found
        if biz_data.group(2) is not None:
            value = float(biz_data.group(2).replace(',', ''))
        else:
            value = None

        # Country
        country = biz_data.group(4) if biz_data.group(4) is not None else ''

        # Date
        value_date = biz_data.group(6) if biz_data.group(6) is not None else ''
        if value_date is not None:
            if len(value_date) > 0:
                # Convert to an appropriate string (YYYY-MM-DD)
                try:
                    date_object = datetime.strptime(value_date, '%d %B %Y')
                    value_date = date_object.strftime('%Y-%m-%d')
                except ValueError:
                    value_date = ''

        # set the return value
        return_val = {'currency': currency,
                      'value': value,
                      'country': country,
                      'value_date': value_date
                      }

    # return what we found (if anything)
    return return_val

