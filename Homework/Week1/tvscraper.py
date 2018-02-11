#!/usr/bin/env python
# Name: Yorick van der Wal
# Student number: 10789014
"""
This script scrapes IMDB and outputs a CSV file with highest rated tv series.
"""

import csv
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import re

TARGET_URL = "http://www.imdb.com/search/title?num_votes=5000,&sort=user_rating,desc&start=1&title_type=tv_series"
BACKUP_HTML = 'tvseries.html'
OUTPUT_CSV = 'tvseries.csv'



def extract_tvseries(dom):
    """
    Extract a list of highest rated TV series from DOM (of IMDB page).
    Each TV series entry should contain the following fields:
    - TV Title
    - Rating
    - Genres (comma separated if more than one)
    - Actors/actresses (comma separated if more than one)
    - Runtime (only a number!)
    """

    # Lists to store the scraped data in
    Titles = []
    Ratings = []
    Genres = []
    Actors = []
    Runtimes = []

    movie_containers = dom.find_all("div", {"class": "lister-item-content"})

    # Extract data from individual movie container
    for container in movie_containers:

        # the title of the serie
        Title = container.h3.a.text
        Titles.append(Title)

        # the IMDB rating of the serie
        Rating = float(container.strong.text)
        Ratings.append(Rating)

        # the genre of the serie
        Genre = container.find('span', class_ = 'genre').get_text(strip=True)
        Genres.append(Genre)

        # the stars of the serie
        Actor = container.find_all('p')[2].find_all('a') 
        Actor_list = []
        
        # itterate over all available actors
        for actorsraw in Actor:
            Actor_list.append(actorsraw.text)    
        Actors.append(Actor_list)


        # the runtime of the episode
        Runtime = container.find('span', class_ = 'runtime').get_text(strip=True)
        Runtimes.append(Runtime)
           
    # return required information
    serie_info = {'Title': Titles, 'Rating': Ratings, 'Genre': Genres, 'Actors': Actors, 'Runtime': Runtimes} 
    return serie_info
 
def save_csv(outfile, tvseries):
    """
    Output a CSV file containing highest rated TV-series.
    """

    # call excel writer
    writer = csv.writer(outfile)

    # create header with appropriate information
    writer.writerow(['Title', 'Rating', 'Genre', 'Actors', 'Runtime'])

    # return values from dictionary
    tvseriesvalues = list(tvseries.values())
    Titles = tvseriesvalues[0]
    Rating = tvseriesvalues[1]
    Genres = tvseriesvalues[2]
    Actors = tvseriesvalues[3]
    Runtime = tvseriesvalues[4]

    # repeat the writing for each title
    for information in range(len(Titles)):

        # Change Actors into a string and enhance
        # overall readability by removing unnecessary 
        # characters
        Actorsstr = str(Actors[information])
        Actorsstr = Actorsstr.replace("[", "")
        Actorsstr = Actorsstr.replace("]", "")
        Actorsstr = Actorsstr.replace("'", "")

        # write the relevant fields into the csv file
        writer.writerow([Titles[information], Rating[information], Genres[information], Actorsstr, Runtime[information]])

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None
    except RequestException as e:
        print('The following error occurred during HTTP GET request to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns true if the response seems to be HTML, false otherwise
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


if __name__ == "__main__":

    # get HTML content at target URL
    html = simple_get(TARGET_URL)

    # save a copy to disk in the current directory, this serves as an backup
    # of the original HTML, will be used in grading.
    with open(BACKUP_HTML, 'wb') as f:
        f.write(html)

    # parse the HTML file into a DOM representation
    dom = BeautifulSoup(html, 'html.parser')

    # extract the tv series (using the function you implemented)
    tvseries = extract_tvseries(dom)

    # write the CSV file to disk (including a header)
    with open(OUTPUT_CSV, 'w', newline='') as output_file:
        save_csv(output_file, tvseries)
