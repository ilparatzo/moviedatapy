from imdb import imdb_loader
from imdb import imdb_helper
import pandas
import logging

logfile = 'movie-logger.log'
open(logfile, 'w').close()
logging.basicConfig(filename=logfile, level=logging.INFO)

# Do a full load
imdb_loader.full_load("f:\\development\\movie_files\\")
# vals = imdb_loader.load_business("Movie", "f:\\development\\movie_files\\business.list")

# i = 1