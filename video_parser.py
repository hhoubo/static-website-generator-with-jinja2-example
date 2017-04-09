from bs4 import BeautifulSoup
import os
import logging
import requests
import urlparse
from multiprocessing import Process, Manager, Pool

ENCODING = 'utf-8'
WORKDIR = '/Users/houbo/workspace/takashimaya/gdw/'
VIDEO_LIST_FILES = ['/Users/houbo/workspace/takashimaya/gdw/qiao.html',
                    '/Users/houbo/workspace/takashimaya/gdw/daban.html',
                    '/Users/houbo/workspace/takashimaya/gdw/hengbin.html',
                    '/Users/houbo/workspace/takashimaya/gdw/jingdu.html',
                    '/Users/houbo/workspace/takashimaya/gdw/xinsu.html'
                    ]
OUTPUT_FILE = '/Users/houbo/workspace/takashimaya/info.txt'
logger = logging.getLogger(__name__)


def make_download_dir(video_list_full_name):
    short_name = video_list_full_name.split('/')[-1]
    dir_name = short_name.split('.')[0]
    logger.debug('dir_name by make_download_dir: %s', dir_name)
    directory = WORKDIR + dir_name
    logger.debug('download_dir by make_download_dir : %s', directory)
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info('download dir is made: %s', directory)
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
            download_dir = make_download_dir(video_list_file)
            logger.debug('download dir: %s', download_dir)
            video_status = _grep_video(WORKDIR + video_page, is_download, download_dir)
            logger.debug('video status: %s', video_status)
        title = a.get_text(strip=True)
        p = video_info.find_all('p')
        release_date = p[0].get_text(strip=True)
        description = p[1].get_text(strip=True)
        line = {'title': title.encode(ENCODING),
                'date': release_date.encode(ENCODING),
                'description': description.encode(ENCODING),
                'video_source': video_status.get('source'),
                'available': video_status.get('available'),
                'size': video_status.get('size')}
        lines.append(line)
    return {'file_name': video_list_file, 'is_download': is_download, 'lines': lines}


def _grep_video(video_page_full_name, is_download, download_folder):
    soup = BeautifulSoup(open(video_page_full_name))
    source = soup.video.source['src'].encode(ENCODING)
    file_name = source.split('/')[-1]
    if urlparse.urlparse(source).scheme != "":
        size = __fetch_size__(source) / 1024 / 1024
        available = size > 0
        if is_download and available:
            __download_video__(source, download_folder, file_name)
    else:
        if os.path.isfile(WORKDIR + source):
            available = True
            size = os.path.getsize(WORKDIR + source) / 1024 / 1024
        else:
            available = False
            size = -1
    return {'source': source, 'available': available, 'size': str(size) + 'M' if size > 0 else 'NON'}


def __fetch_size__(source):
    response = requests.head(source)
    if response.ok:
        logger.debug('response header content-length: %s', response.headers.get('content-length'))
        size = int(float(response.headers.get('content-length')))
    else:
        size = -1
    return size


def __download_video__(source_url, local_path, file_name):
    file_size = __fetch_size__(source_url)
    file_full_name = local_path + '/' + file_name
    if os.path.isfile(file_full_name):
        if os.path.getsize(file_full_name) == file_size :
            logger.info('The file %s is exist', file_full_name)
        else:
            __do_download__(source_url, file_full_name)
    else:
        __do_download__(source_url, file_full_name)


def __do_download__(source_url, file_full_name):
    with open(file_full_name, 'wb') as handle:
        response = requests.get(source_url, stream=True)
        if response.ok:
            for block in response.iter_content(1024):
                handle.write(block)
        else:
            logger.error('Can not download the file %s', source_url)


def info_record(video_info, output_file):
    logger.debug(video_info)
    with open(output_file, 'a+') as output:
        output.write(video_info['file_name'] + '\n')
        output.write(
            'Download the video from CDN\n' if video_info['is_download'] else 'NOT Download the video from CDN\n')
        for line in video_info['lines']:
            output.write('{0}  {1}  {2} {3} {4} {5}\n'.format(
                line.get('available'),
                line.get('size'),
                line.get('title'),
                line.get('date'),
                line.get('description'),
                line.get('video_source')
            ))
        output.write('\n')


if __name__ == "__main__":
    FORMAT = '%(asctime)s  %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    for video_list_page in VIDEO_LIST_FILES:
        info = grep_info(video_list_page, True)
        info_record(info, OUTPUT_FILE)
