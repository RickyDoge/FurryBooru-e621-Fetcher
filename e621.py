import sys
import re
from downloader import Downloader
from bs4 import BeautifulSoup


def main(webpage_url: str, mode: str):
    downloader = Downloader()
    num_downloaded = 0
    if webpage_url[-1] == '/':
        webpage_url = webpage_url[:len(webpage_url) - 1]

    while True:
        # get and decode html, and then download images
        html = downloader.get_html(webpage_url)
        soup = BeautifulSoup(html, features="lxml").find('div', id="posts-container")
        articles = soup.find_all('article', attrs={'id': True})
        image_urls = []
        for i, article in enumerate(articles):
            article_id = article['id'][5:]
            url = 'https://e621.net/posts/' + article_id
            img_soup = BeautifulSoup(downloader.get_html(url), features="lxml")
            img_url = img_soup.find('a', class_=re.compile('^button'))['href']
            img_fname = [url.split('/')[-1] for url in image_urls]

            image_urls.append(img_url)
            downloader.create_download_task(img_url, img_fname)
            downloader.print_process(webpage_url, num_downloaded, i + 1)

        if len(image_urls) == 0:
            break

        # wait until all download processes complete
        downloader.wait(webpage_url, num_downloaded, len(image_urls))
        num_downloaded += len(image_urls)
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


if __name__ == '__main__':
    num_para = len(sys.argv)
    if len(sys.argv) <= 1:
        raise Exception("Please input the target web url.")
    url = sys.argv[1]
    mode = "MULTI_PAGE" if len(sys.argv) <= 2 or sys.argv[2] != 'one' else "ONE_PAGE"
    main(webpage_url=url, mode=mode)
