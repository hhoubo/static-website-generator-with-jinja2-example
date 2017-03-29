from bs4 import BeautifulSoup
import os
import logging
import requests
import urlparse

ENCODING = 'utf-8'
WORKDIR = '/home/hou-b/Develop/WorkSpace/sandbox/gdw/'
VIDEO_LIST_FILES = ['/home/hou-b/Develop/WorkSpace/sandbox/gdw/qiao.html',
                    # '/home/hou-b/Develop/WorkSpace/sandbox/gdw/daban.html',
                    '/home/hou-b/Develop/WorkSpace/sandbox/gdw/hengbin.html',
                    # '/home/hou-b/Develop/WorkSpace/sandbox/gdw/jingdu.html',
                    # '/home/hou-b/Develop/WorkSpace/sandbox/gdw/xinsu.html',
                    ]
OUTPUT_FILE = '/home/hou-b/Develop/WorkSpace/sandbox/gdw/info.txt'
logger = logging.getLogger(__name__)


def make_download_dir(video_list_full_name):
    short_name = video_list_full_name.split('/')[-1]
    dir_name = short_name.split('.')[0]
    directory = os.path.dirname(WORKDIR + dir_name)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


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
            video_status = _grep_video(WORKDIR + video_page, is_download, make_download_dir(video_list_file))
            logger.debug('video status: %s', video_status)
        title = a.get_text(strip=True)
        p = video_info.find_all('p')
        release_date = p[0].get_text(strip=True)
        description = p[1].get_text(strip=True)
        line = {'title': title.encode(ENCODING),
                'date': release_date.encode(ENCODING),
                'description': description.encode(ENCODING),
                'video_source': video_status.get('source'),
                'available': video_status.get('available')}
        lines.append(line)
    return {'file_name': video_list_file, 'is_download': is_download, 'lines': lines}


def _grep_video(videp_page_full_name, is_download, download_folder):
    soup = BeautifulSoup(open(videp_page_full_name))
    source = soup.video.source['src'].encode(ENCODING)
    file_name = source.split('/')[-1]
    if urlparse.urlparse(source).scheme != "":
        if is_download:
            with open(os.path.join(download_folder + '/', file_name), 'wb') as handle:
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
    else:
        if os.path.isfile(WORKDIR + source):
            available = True
        else:
            available = False
    return {'source': source, 'available': available}


def write(video_info, output_file):
    logger.debug(video_info)
    with open(output_file, 'a+') as output:
        output.write(video_info['file_name'] + '\n')
        output.write(
            'Download the video from CDN\n' if video_info['is_download'] else 'NOT Download the video from CDN\n')
        for line in video_info['lines']:
            output.write('{0}  {1}  {2} {3} {4}\n'.format(
                line.get('title'),
                line.get('date'),
                line.get('description'),
                line.get('video_source'),
                line.get('available')))
        output.write('\n')


if __name__ == "__main__":
    FORMAT = '%(asctime)s  %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    for video_list_page in VIDEO_LIST_FILES:
        info = grep_info(video_list_page, False)
        write(info, OUTPUT_FILE)
