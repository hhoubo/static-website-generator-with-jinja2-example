from bs4 import BeautifulSoup
import os
import logging
import requests

ENCODING = 'utf-8'
WORKDIR = '/home/hou-b/Develop/WorkSpace/sandbox/gdw/'
VIDEO_LIST_FILE = '/home/hou-b/Develop/WorkSpace/sandbox/gdw/hengbin.html'
OUTPUT_FILE = '/home/hou-b/Develop/WorkSpace/sandbox/gdw/info.txt'
VIDEO_DOWNLOAD = '/home/hou-b/Develop/WorkSpace/sandbox/gdw/hengbin/'
logger = logging.getLogger(__name__)


def grep_info(video_list_file, is_download):
    soup = BeautifulSoup(open(video_list_file))
    lines = []
    for video_info in soup.select('div.shopInfo'):
        a = video_info.h3.a
        video_page = a['href'].encode(ENCODING)
        video_status = {'source': '', 'available': ''}
        logger.debug('video_page: %s', video_page)
        logger.debug('video_page is exist: %s', os.path.isfile(WORKDIR + video_page))
        if video_page and os.path.isfile(WORKDIR + video_page):
            video_status = _grep_video(WORKDIR + video_page, is_download, VIDEO_DOWNLOAD)
            logger.debug('video status: %s', video_status)
        title = a.get_text(strip=True)
        p = video_info.find_all('p')
        release_date = p[0].get_text(strip=True)
        description = p[1].get_text(strip=True)
        line = {'title': title.encode(ENCODING),
                'date': release_date.encode(ENCODING),
                'description':description.encode(ENCODING),
                'video_source': video_status.get('source'),
                'available': video_status.get('available')}
        lines.append(line)
    return lines


def _grep_video(videp_page_full_name, is_download, download_folder):
    soup = BeautifulSoup(open(videp_page_full_name))
    source = soup.video.source['src'].encode(ENCODING)
    file_name = source.split('/')[-1]
    if is_download:
        with open(download_folder + file_name, 'wb') as handle:
            response = requests.get(source, stream=True)
            if response.ok:
                for block in response.iter_content(1024):
                    handle.write(block)
                available = True
            else:
                available = False
    else:
        response = requests.head(source)
        available = response.ok
    return {'source': source, 'available': available}


def write(lines, output_file):
    output = open(output_file, 'w+')
    try:
        for line in lines:
            output.write('{0}  {1}  {2} {3} {4}\n'.format(
                line.get('title'),
                line.get('date'),
                line.get('description'),
                line.get('video_source'),
                line.get('available')))
    finally:
        output.close()

if __name__ == "__main__":
    FORMAT = '%(asctime)s  %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    lines = grep_info(VIDEO_LIST_FILE, True)
    write(lines, OUTPUT_FILE)
