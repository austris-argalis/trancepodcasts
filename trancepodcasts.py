import re
from robobrowser import RoboBrowser
from urllib.parse import unquote
import os
import argparse
import zipfile

def find_download_page(podcast, episode):
    download_base = 'https://www.trancepodcasts.com/download/'
    browser = RoboBrowser(history=True)
    browser.open('https://www.trancepodcasts.com/download/{:s}-{:d}/'.format(podcast, episode))

    link = browser.find('a', attrs = {'rel': 'nofollow', 'class': 'btn'})
    browser.follow_link(link)
    browser.response

def get_podcast_download_url(podcast, episode):
    return 'http://files.trancepodcasts.co.uk/72733810498CL/Tiesto%20-%20Club%20Life%20Episode%20{:d}.zip'.format(
        episode)


def get_downloadable_urls(episodes, podcast='cl'):
    episodes = list(map(lambda x: int(x), episodes))
    # if only one episode
    if len(episodes) == 1:
        episodes.append(episodes[0] + 1)  # for range to work need one value higher

    url_accumulator = []
    for episode in range(episodes[0], episodes[1]):
        url_accumulator.append(get_podcast_download_url(podcast, episode))

    return url_accumulator


def download(url, path):
    browser = RoboBrowser(history=True)
    request = browser.session.get(url, stream=True)

    # last part of url containing .zip
    filename = unquote(url.split('/')[-1])

    filepath = path + "/" + filename.replace('//', '/')
    print('Downloading: {:s}'.format(filename))
    with open(filepath, "wb") as zip_file:
        zip_file.write(request.content)

    print('File saved to: {:s}'.format(filepath))
    return filepath


def main(args):
    episodes = args.episodes.split('-')
    path = args.path if args.path != None else os.getcwd()

    for url in get_downloadable_urls(episodes):
        filepath = download(url, path)


    print('Done')


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Download trancepodcasts.co.uk")
    parser.add_argument('episodes', metavar='EPISODE', help="Episode number or %%-%% if multiple")
    parser.add_argument('-p', '--path', required=False, help="File save path")
    parser.add_argument("-z", "--unzip", help="Unzip downloaded archives")
    args = parser.parse_args()
    main(args)