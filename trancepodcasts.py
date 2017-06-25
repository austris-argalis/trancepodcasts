#!/usr/bin/env python3

from robobrowser import RoboBrowser
from urllib.parse import unquote
import os
import argparse
import subprocess
from zipfile import ZipFile

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

    return filepath


def mp3val(folder):
    for file in os.listdir(folder):
        if file.endswith(".mp3"):
            mp3file = os.path.join(folder, file)
            command = 'mp3val -f -t "{:s}"'.format(mp3file)
            try:
                subprocess.call(command, shell=True)
            except FileNotFoundError:
                print('mp3val command not found')


def main(args):
    episodes = args.episodes.split('-')
    path = args.path if args.path != None else os.getcwd()

    for url in get_downloadable_urls(episodes):
        # TODO check if directory exists
        filepath = download(url, path)
        folder = filepath.replace('.zip', '')
        if (args.nozip):
            with ZipFile(filepath, 'r') as zip:
                print('Extracting...')
                zip.extractall(folder)
                print('Extracted to: {:s}'.format(folder))
            os.remove(filepath)

            if (args.mp3fix):
                mp3val(folder)


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Download trancepodcasts.co.uk")
    parser.add_argument('episodes', metavar='EPISODE', help="Episode number or %%-%% if multiple")
    parser.add_argument('-p', '--path', required=False, help="File save path")
    parser.add_argument("-z", "--nozip", action='store_false', help="Do not unzip downloaded archives")
    parser.add_argument("-m", "--mp3fix", action='store_true', help="Try and fix file with mp3val")
    args = parser.parse_args()
    main(args)
