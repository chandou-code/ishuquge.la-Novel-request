import requests
from bs4 import BeautifulSoup
import re
import os
import logging


class Novel:
    def __init__(self, search_key: str):
        self.book_thename = None
        self.search_key = search_key
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.50',
            'Referer': 'https://www.ishuquge.la/',
            'Origin': 'https://www.ishuquge.la'
        }

    def sanitize_filename(self, filename: str) -> str:
        illegal_chars = '[<>:"/\\\|?*]'
        sanitized_name = re.sub(illegal_chars, "", filename)
        return sanitized_name

    def get_search_list(self, search_key: str) -> dict:
        url = 'https://www.ishuquge.la/search.php'
        data = {'s': '6445266503022880974', 'searchkey': search_key}
        response = requests.post(url, data=data, headers=self.headers)
        encoding = response.encoding if "charset" in response.headers.get("content-type", "").lower() else None
        soup = BeautifulSoup(response.content, "html.parser", from_encoding=encoding)

        td_list = soup.find_all('div', class_='bookinfo')
        links = {}
        for td in td_list:
            a_tag = td.find('a')
            if a_tag:
                link = a_tag['href']
                name = a_tag.get_text().strip()
                links[link] = name
                # print(name)

        return links

    def get_index(self, book_url: str) -> dict:
        url = f'https://www.ishuquge.la{book_url}'
        key = book_url.split('/')[2]
        response = requests.get(url, headers=self.headers)
        encoding = response.encoding if "charset" in response.headers.get("content-type", "").lower() else None
        soup = BeautifulSoup(response.content, "html.parser", from_encoding=encoding)
        td_list = soup.find_all('dd')[12:]
        links = {}
        for td in td_list:
            a_tag = td.find('a')
            if a_tag:
                link = a_tag['href']
                name = self.sanitize_filename(a_tag.get_text().strip())
                links[link] = name
        return links, key

    def get_detail_html(self, url: str, key: str) -> list:
        url = f'https://www.ishuquge.la/txt/{key}/{url}'
        response = requests.get(url, headers=self.headers)
        encoding = response.encoding if "charset" in response.headers.get("content-type", "").lower() else None
        soup = BeautifulSoup(response.content, "html.parser", from_encoding=encoding)
        br_tags = soup.find_all('br')
        for tag in br_tags:
            tag.decompose()
        text = soup.prettify()
        # print(text)
        pattern = r'最新网址(.*?)请记住本书首发域名'
        result = re.findall(pattern, text, re.S)
        # print(result)
        self.result = result[0].split("\n")
        del self.result[0:3]
        del self.result[-2:]
        # print(self.result)
        return self.result

    def download_html(self, text: str, filename: str,bookname):
        text = text.replace("     ", "")
        current_path = os.path.dirname(os.path.abspath(__file__))
        download_dir = os.path.join(current_path, 'download')
        cc_dir = os.path.join(download_dir, f'{bookname}')

        if not os.path.exists(cc_dir):
            os.makedirs(cc_dir)

        # 打开文件并写入内容
        with open(os.path.join(cc_dir, f'{filename}.txt'), 'w', encoding="utf-8") as f:
            f.write(text)



    def start(self):
        try:
            # 获取搜索结果
            result_dict = self.get_search_list(self.search_key)
            logging.info(f"共找到{len(result_dict)}本小说，搜索结果如下：")
            if not result_dict:  # 如果result_dict为空字典，则提示用户未找到相关小说信息
                print("未找到相关小说信息，请重新输入")
                return

            for i, book_name in enumerate(result_dict.values(), start=1):
                print(f"{i}. <<{book_name}>>")
            print("输入书名前的标号")
            # 选择一本小说并获取目录
            book = int(input())

            book_url = list(result_dict.keys())[book - 1]

            index_dict, key = self.get_index(book_url)
            self.book_thename=self.sanitize_filename(result_dict[book_url])
            logging.info(f"已选择小说《{result_dict[book_url]}》，共{len(index_dict)}章")

            # 下载每个章节的内容
            for url, title in index_dict.items():
                logging.info(f"正在下载章节：{title}")
                # print(result_dict[book_url])
                contents = self.get_detail_html(url, key)
                new_string = ''.join(contents)
                self.download_html(new_string, title,result_dict[book_url])

            logging.info("小说下载完成")
        except Exception as e:
            logging.exception(e)
            logging.error("小说下载失败")
if __name__ == '__main__':
    # 设置日志记录器
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] [%(message)s]")
    logging.info(f"小说下载 by纯度official")
    logging.info(f"输入书名")
    book = str(input())
    # 创建小说对象，传入搜索关键词并启动
    n1 = Novel(search_key=book)
