import os
import time
import urllib3
import logging
from multiprocessing import Pool, Manager
from urllib.request import urlretrieve


def download_file(file_url, fname, shared_value, shared_lock, logger):
    attempt = 0
    while attempt <= 3:  # max attempt 3 times
        try:
            fpath = os.path.join(os.curdir, 'download')
            if not os.path.exists(fpath):
                os.mkdir(fpath)
            fpath = os.path.join(fpath, fname)
            urlretrieve(file_url, fpath)
            break
        except:
            attempt += 1

    shared_lock.acquire()
    shared_value.value = shared_value.value - 1
    if attempt > 3:
        logger.info("Cannot download file {}".format(file_url))
    shared_lock.release()


class Downloader:
    def __init__(self, num_processes=4):
        self.userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                         'Chrome/97.0.4692.71 Safari/537.36'
        self.__manager = Manager()
        self.__http_pool = urllib3.PoolManager(timeout=10)
        self.__logger = Downloader.get_logger()
        self.__processes_pool = Pool(num_processes)
        self.__semap = self.__manager.Value(typecode="i", value=0)
        self.__lock = self.__manager.Lock()

    def get_html(self, url):
        try:
            response = self.__http_pool.request('get', url, headers={'user-agent': self.userAgent})
            html = response.data.decode('utf-8')
            return html
        except:
            self.__logger.warning("Cannot connect to {}".format(url))

    def create_download_task(self, file_url, fname):
        assert self.__semap.value >= 0
        self.__lock.acquire()
        self.__semap.value = self.__semap.value + 1
        self.__lock.release()
        self.__processes_pool.apply_async(download_file, args=(file_url, fname,
                                                               self.__semap,
                                                               self.__lock,
                                                               self.__logger))

    def wait(self, webpage_url, downloaded_num, downloading_num):
        while True:
            if self.__semap.value == 0:
                break
            time.sleep(1)
            self.print_process(webpage_url, downloaded_num, downloading_num)
        self.print_process(webpage_url, downloaded_num, downloading_num)
        print()

    def close(self):
        self.__processes_pool.close()
        self.__processes_pool.join()

    def print_process(self, webpage_url, downloaded_num, downloading_num):
        _downloaded_num = downloaded_num + downloading_num - self.__semap.value
        print('\rURL: {}/ {} files have been downloaded.'.format(webpage_url, _downloaded_num), end='')

    @staticmethod
    def get_logger():
        logger = logging.getLogger()
        logger.setLevel(level=logging.INFO)
        handler = logging.FileHandler("log.log")
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
