# -------------------------------------------------------------------
#  INSTRUCTIONS
# -------------------------------------------------------------------
# Packages needed:
#   time
#   requests
#   beautifulsoup4
#   os

# Package install in terminal window:
#   pip install 'PackageName'
#   note: single quotes aren't required
# -------------------------------------------------------------------
#  Usage:
#   pass search queries to the communication pipe (default defined as
#   global var). Formatting is 'query:enter search query here'
# -------------------------------------------------------------------
# Original application for tv show watchlist tracker.
#   pre-programmed to bias results from Rotten Tomatoes and to ShowsImages
#   directory

# Can modify communication pipe global variable:
#   COMM_PIPE
#   note: communication pipe text file defined as local to program directory;

# Can modify results to new application updating global variable:
#   QUERY_RELEVANCE
#   note: designed to handle full string input with spaces

# Can modify destination directory global variable:
#   DEST_DIR
#   note: destination directory defined as local to program directory;
#           potential future implementation to easily update and read
#           with 'os' module

# Can modify standard wait time global variable:
#   STD_WAIT
#   note: default 5 seconds
# -------------------------------------------------------------------

import time
import requests
import os
from bs4 import BeautifulSoup


# GLOBAL DECLARATIONS
# communication pipe
COMM_PIPE = 'image-service.txt'
# relevance to add to query results
QUERY_RELEVANCE = 'rotten tomatoes'
# destination directory to save images
DEST_DIR = 'ShowsImages'
# std. wait duration
STD_WAIT = 5.0


def main() -> None:
    """
    Continuous runs checking a communication pipe for a requested image. When
    prompted in image-service.txt:
        -reads the show title
        -searches for representative image on internet
        -downloads image to local directory
        -writes path to image to COMM_PIPE

    :return: None
    """
    validate_comm_pipe()
    validate_dest_dir()

    while True:
        read_contents = read_pipe()
        if not read_contents:
            continue

        if ':' not in read_contents:
            format_error()
            continue

        query_check, read_title = split_contents(read_contents)

        if query_check != 'query':
            print('waiting')
            time.sleep(STD_WAIT)
            continue
        else:
            query_title = parse_title(read_title)
            img_source = scrape_image(query_title)

            path = download_to_dir(img_source, query_title)

            write_to_pipe(f'path:{path}')
            print('Success')
            continue


def scrape_image(query_title: str) -> str:
    """
    When called, searches provided show_title query on internet, downloads
    image to directory, and returns image path.

    :param: show_title(str): title of show to find representative image of.
    :return: parsed_source(str): html source for image
    """
    relevance_parsed, sourcing_parsed = parse_relevance()

    google_URL = create_google_url(relevance_parsed, query_title)

    google_content = get_google_content(google_URL)

    google_links = get_content_links(google_content)

    sourcing_URLs = parse_links(google_links, sourcing_parsed)

    source_content = get_source_content(sourcing_URLs[0])

    unparsed_source_links = gen_source_links(source_content)

    parsed_source = parse_source_links(unparsed_source_links)

    return parsed_source


def validate_comm_pipe() -> None:
    """
    Checks if COMM_PIPE exists in local directory. If it doesn't, file is created.

    :return:
    """
    if not os.path.isfile(f"./{COMM_PIPE}"):
        with open(f"./{COMM_PIPE}") as cf:
            pass
        cf.close()


def validate_dest_dir() -> None:
    """
    Checks if DEST_DIR exists in local directory. If it doesn't, directory is created.

    :return: None
    """
    if not os.path.isdir(f"./{DEST_DIR}"):
        os.mkdir(f"./{DEST_DIR}")


def read_pipe() -> str:
    """
    Opens COMM_PIPE and reads current contents.

    :return: (str) current string contents of file.
    """
    with open(f"./{COMM_PIPE}", 'r') as is_file:
        read_file = is_file.readline()
    is_file.close()
    return read_file


def format_error() -> None:
    """
    Writes to pipe that passed communication in COMM_PIPE didn't meet
    formatting requirements and waits 5 seconds.

    :return: None
    """
    format_err = "Communication not meeting format 'type:value'"
    write_to_pipe(format_err)
    print('format error')
    time.sleep(STD_WAIT)


def split_contents(read_contents: str) -> tuple:
    """
    Takes read contents from pipe and splits into two parts for parsing.

    :return: (tuple) tuple of strings for split read contents.
    """
    split_read = read_contents.split(":", 1)
    return split_read[0], split_read[1]


def parse_title(read_title: str) -> str:
    """
    Takes entered title information and parses contents to google search formatting.

    :param read_title: (str) entered title information.
    :return: (str) title parsed to google search formatting.
    """
    query_title = read_title.replace(' ', '+')
    return query_title


def download_to_dir(img_source: str, query_title: str) -> str:
    """
    Takes image source url and query title, downloads image to defined directory, and names
    image file as specified. Returns path to file.

    :param img_source: (str) image source URL.
    :param query_title: (str) query title name.
    :return: None
    """
    pic_file = f'./{DEST_DIR}/{query_title}.jpg'

    response = requests.get(img_source)
    with open(pic_file, 'wb') as new_pic:
        new_pic.write(response.content)
        new_pic.flush()
        os.fsync(new_pic.fileno())
    new_pic.close()
    return pic_file


def write_to_pipe(communication: str) -> None:
    """
    Takes query title information and write downloaded image path to COMM_PIPE.

    :param communication: (str) title parsed to google search formatting.
    :return: None
    """
    with open(f"./{COMM_PIPE}", 'w') as out_file:
        out_file.write(communication)
    out_file.close()


def parse_relevance() -> tuple:
    """
    Parse global relevance variable to google query format and page sourcing format.

    :return: (tuple) parsed str values for relevance and sourcing.
    """
    if ' ' in QUERY_RELEVANCE:
        relevance_parsed = QUERY_RELEVANCE.replace(' ', '+')
        sourcing_parsed = QUERY_RELEVANCE.replace(' ', '')
    else:
        relevance_parsed, sourcing_parsed = QUERY_RELEVANCE
    return relevance_parsed, sourcing_parsed


def create_google_url(relevance_parsed: str, query_title: str) -> str:
    """
    Takes parsed relevance and query title variables and creates a google search query URL.

    Note: if a different search engine is used, search query URL might have different
            different formatting; requiring you to update URL format.

    :return: (str) google search query URL.
    """
    google_URL = f"https://www.google.com/search?q={relevance_parsed}+{query_title}"
    return google_URL


def get_google_content(google_URL: str) -> str:
    """
    Take google_URL, parse HTML content, and return content from the page.

    :param google_URL: (str) google search query URL.
    :return: (str) parsed content of html google search query.
    """
    google_HTML = requests.get(google_URL)
    google_content = BeautifulSoup(google_HTML.content, 'html.parser')
    return google_content


def get_content_links(google_content: str) -> str:
    """

    :param google_content: (str) parsed content of html google search query.
    :return:
    """
    # find all 'a' tags which include page links
    google_links = google_content.find_all('a')
    return google_links


def parse_links(google_links: str, sourcing_parsed: str) -> list:
    """
    Parse links on google search query and add each to a list.

    :param google_links: (str) links from google search page content.
    :param sourcing_parsed: (str) sourcing relevance variable parsed.
    :return: (list) list of links from google search query page.
    """
    sourcing_URLs = list()
    for URL in google_links:
        if f'{sourcing_parsed}' in URL['href']:
            st_idx = 7
            end_idx = URL['href'].find('&')
            sourcing_URLs.append(URL['href'][st_idx:end_idx])
    return sourcing_URLs


def get_source_content(source_URL: str) -> str:
    """
    Take source_URL, parse HTML content, and return content from the page.

    :param source_URL: (str) source query URL.
    :return: (str) parsed content of html source query.
    """
    source_HTML = requests.get(source_URL)
    source_content = BeautifulSoup(source_HTML.content, 'html.parser')
    return source_content


def gen_source_links(source_content: str) -> list:
    """
    Take source content find all image source links and append to a list.

    Note:  if you're adapting to another application, inspect your source page's
            classes and update source_class to source's relevant HTML class

    :param source_content: (list) list of string source links.
    :return: (list) list of image source links
    """
    source_class = 'PhotosCarousel__image'
    unparsed_source_links = list()
    page_images = source_content.find_all('img')
    for tag in page_images:
        if 'class' in tag.attrs and tag['class'] == [source_class]:
            unparsed_source_links.append(tag['src'])
    return unparsed_source_links


def parse_source_links(unparsed_source_links: list) -> str:
    """
    Parse first image link in list of unparsed image source links and
    return a parsed link to the image for downloading.

    Note:  check if source link has a resizing page prepended to source
            if you're adapating to another application, inspect your source
            looking for its resizing and resizing delimiter if necessary

    :param unparsed_source_links: (list) list of image source links
    :return: (str) parsed source link to image for downloading.
    """
    if 'resiz' in unparsed_source_links[0]:
        st_idx = unparsed_source_links[0].find('v2/') + 3
        parsed_source = unparsed_source_links[0][st_idx:]
    else:
        parsed_source = unparsed_source_links[0]

    return parsed_source


if __name__ == "__main__":
    main()
