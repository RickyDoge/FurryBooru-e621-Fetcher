import sys
import re
from downloader import Downloader
from bs4 import BeautifulSoup


def main(webpage_url: str, mode: str):
    downloader = Downloader()
    num_downloaded = 0
    while True:
        # get html and decode
        html = downloader.get_html(webpage_url)
        image_urls, image_fnames = decode_html(html)

        if len(image_urls) == 0:
            break

        # multiprocessing downloading images (default: 4), you can modify num_processes in downloader.py
        for image_url, fname in zip(image_urls, image_fnames):
            downloader.create_download_task(image_url, fname)

        # wait until all download processes complete
        downloader.wait(webpage_url, num_downloaded, len(image_urls))
        num_downloaded += len(image_urls)
        print('\r{}/ {} images have been downloaded.'.format(webpage_url, num_downloaded), end='')
        if mode == "ONE_PAGE":
            break

        # iteratively page_num plus one
        page = None
        query_string = re.split("[%?&]", webpage_url)
        for para in query_string:
            page = re.search("page=\d+", para)
            if page is not None:
                page = int(page.group()[5:])
                break

        if page is None:
            webpage_url = webpage_url + "&page=2"
        else:
            webpage_url = re.sub("page=\d+", "page={}".format(page + 1), webpage_url)

    downloader.close()


def decode_html(html):
    img_elements = BeautifulSoup(html, features="lxml").find_all('img', class_="has-cropped-false")
    image_urls = [img_ele['src'].replace('/preview', '') for img_ele in img_elements]
    image_fnames = [url.split('/')[-1] for url in image_urls]
    return image_urls, image_fnames


if __name__ == '__main__':
    num_para = len(sys.argv)
    if len(sys.argv) <= 1:
        raise Exception("Please input the target web url.")
    url = sys.argv[1]
    mode = "MULTI_PAGE" if len(sys.argv) <= 2 or sys.argv[2] != 'one' else "ONE_PAGE"
    main(webpage_url=url, mode=mode)
