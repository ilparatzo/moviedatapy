#!/usr/bin/env bash

# Movies
curl -o "/data/development/movie_files/movies.list.gz" "ftp://ftp.fu-berlin.de/pub/misc/movies/database/movies.list.gz"
gunzip "/data/development/movie_files/movies.list.gz"

# Language
curl -o "/data/development/movie_files/language.list.gz" "ftp://ftp.fu-berlin.de/pub/misc/movies/database/language.list.gz"
gunzip "/data/development/movie_files/language.list.gz"

# Genres
curl -o "/data/development/movie_files/genres.list.gz" "ftp://ftp.fu-berlin.de/pub/misc/movies/database/genres.list.gz"
gunzip "/data/development/movie_files/genres.list.gz"

# Business
curl -o "/data/development/movie_files/business.list.gz" "ftp://ftp.fu-berlin.de/pub/misc/movies/database/business.list.gz"
gunzip "/data/development/movie_files/business.list.gz"

# Actors
curl -o "/data/development/movie_files/actors.list.gz" "ftp://ftp.fu-berlin.de/pub/misc/movies/database/actors.list.gz"
gunzip "/data/development/movie_files/actors.list.gz"

# Actresses
curl -o "/data/development/movie_files/actresses.list.gz" "ftp://ftp.fu-berlin.de/pub/misc/movies/database/actresses.list.gz"
gunzip "/data/development/movie_files/actresses.list.gz"

# Directors
curl -o "/data/development/movie_files/directors.list.gz" "ftp://ftp.fu-berlin.de/pub/misc/movies/database/directors.list.gz"
gunzip "/data/development/movie_files/directors.list.gz"

# Producers
curl -o "/data/development/movie_files/producers.list.gz" "ftp://ftp.fu-berlin.de/pub/misc/movies/database/producers.list.gz"
gunzip "/data/development/movie_files/producers.list.gz"

# Miscellaneous
curl -o "/data/development/movie_files/miscellaneous.list.gz" "ftp://ftp.fu-berlin.de/pub/misc/movies/database/miscellaneous.list.gz"
gunzip "/data/development/movie_files/miscellaneous.list.gz"
