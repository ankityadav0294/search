import scrapy.spiders
import urlparse
from bs4 import BeautifulSoup
from whoosh.fields import *
from whoosh.analysis import StemmingAnalyzer, CharsetFilter
from whoosh.support.charset import default_charset, charset_table_to_dict
import hashlib
import os, os.path
from whoosh import index
import re
import requests
from spiderman.items import MyItem
from ast import literal_eval


class fourthspider(scrapy.Spider):
    name = '4spider'
    allowed_domains = [
        'iitg.ernet.in',
        'iitg.ac.in'
    ]
    start_urls = [
        "http://intranet.iitg.ernet.in/",
        "http://repo.cse.iitg.ernet.in/index.php/apps/files/",
        "http://iitg.ac.in/"
    ]

    def __init__(self):
        if not os.path.exists("indexdir"):
            os.mkdir("indexdir")

        charmap = charset_table_to_dict(default_charset)
        my_analyzer = StemmingAnalyzer() | CharsetFilter(charmap)

        schema = Schema(url=ID(stored=True),
                        title=TEXT(stored=True),
                        content=TEXT(stored=True, spelling=True),
                        tags=KEYWORD(stored=True),
                        urlid=STORED)

        self.ix = index.create_in("indexdir", schema)
        self.writer = self.ix.writer()
        self.logger.info("Writer created")
        self.regexp = [
            # re.compile(r'www\.iitg\.ernet\.in'),
            re.compile(r'iitg\.ernet\.in/news'),
            re.compile(r'(&|\?)month=\d+'),
            re.compile(r'(&|\?)year=\d+'),
            re.compile(r'(&|\?)day=\d+'),
            re.compile(r'(&|\?)week=\d+'),
            # re.compile(r'http://iitg\.ernet\.in'),
            re.compile(r'(((\?|&)sort=)|((\?|&)order=))'),
            re.compile(r'/activities/all-events/(.)+'),
            re.compile(r'(csea/Public\/web_new\/index\.php/activities/others)'),
            re.compile(r'calendar'),
            re.compile(r'\d\d\d\d/\d\d/\d\d'),
            re.compile(r'\?C=(.);O=(.)'),
            re.compile(r'\d\d\d\d-\d\d-\d\d'),
            re.compile(r'/eventcal/'),
            re.compile(r'week/\d\d\d\d-W\d+'),
            re.compile(r'nptel\.iitg\.ernet\.in'),

        ]

        self.crawled_hash = []
        self.files = open('indexed_files.txt', 'w')
        self.ignored = open('ignored.txt', 'w')
        self.inurls = open('inurls.txt', 'w')

    def close(self, spider, reason):
        self.logger.info("Commited Changes to indexing")
        self.writer.commit()
        self.files.close()
        self.ignored.close()
        self.inurls.close()
        return scrapy.Spider.close(spider, reason)

    def parse(self, response):

        try:
            soup = BeautifulSoup(response.selector.xpath('//html').extract()[0], 'html5lib')
        except:
            referer = response.request.headers.get('Referer', None)
            self.index_file(referer, response.url)
            self.logger.info('file referer %s', referer)
            return

        plain_text = soup.prettify()
        plain_text = plain_text.encode('ascii', 'ignore')
        m = hashlib.sha1(str(plain_text)).hexdigest()
        if str(m) not in self.crawled_hash:
            self.crawled_hash.append(str(m))
        else:
            self.ignored.write(response.url + '     hash' + '\n')
            return

        urls = []

        data = self.parse_data(response, m)

        item = MyItem()
        try:
            item['url'] = data['url']
            item['content'] = data['content']
            item['tags'] = data['tags']
            item['title'] = data['title']
            item['urlid'] = data['urlid']
            self.inurls.write(response.url + ' \n')
            yield {'url': item['url']}
        except:
            pass
        for url in response.selector.xpath('//a/@href').extract():
            if url.endswith('#'):
                continue
            url = urlparse.urljoin(response.url, url.strip())
            if all((reg.search(url) is None) for reg in self.regexp):
                urls.append(url)
            else:
                self.ignored.write(response.url + '     regex' + '\n')

        for url in urls:
            self.logger.info('========== visiting url %s !!', url)
            yield scrapy.Request(url, callback=self.parse)

    def parse_data(self, response, m):

        soup = BeautifulSoup(response.selector.xpath('//html').extract()[0], 'html5lib')
        title = soup.title.string
        # content = soup.get_text()
        texts = soup.findAll(text=True)
        content = filter(visible, texts)
        temp = ''
        for s in content:
            try:
                temp += ' ' + unicode(literal_eval("'%s'" % s))
            except:
                continue
        content = temp
        tags = ""
        try:
            for h in soup.findAll(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7']):
                try:
                    tags = tags + " " + h.string
                except:
                    continue
        except:
            pass

        title = unicode(title)
        tags = unicode(tags)
        # content = unicode(content)
        url = unicode(response.url)
        urlid = unicode(str(m))
        try:
            self.writer.add_document(url=url, title=title, content=content, tags=tags, urlid=urlid)
        except:
            return
        self.logger.info("added To whoosh")
        return {'url': url, 'title': title, 'content': content, 'tags': tags, 'urlid': urlid}

    def index_file(self, referer, url):
        try:
            source_code = requests.get(referer)
        except:
            return
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text, "lxml")

        for link in soup.findAll('a'):
            href = link.get('href')
            if not url.endswith(href):
                continue

            r = requests.get(url)
            if "text/html" in r.headers["content-type"]:
                continue
            title = ''
            content = ''

            try:
                title = link.string + ' ' + href
            except:
                title = href

            try:
                content = link.find_parent("tr").get_text() + title
            except:
                content = title

            # temp = ''
            # try:
            #     for s in content:
            #         try:
            #             temp += ' ' + unicode(literal_eval("'%s'" % s))
            #         except:
            #             continue
            #     content = temp
            # except:
            #     continue

            self.files.write(url + '\n')
            self.logger.info("file To whoosh")
            try:
                self.writer.add_document(url=unicode(url), title=unicode(title), content=unicode(content))
            except:
                return

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', element.encode('ascii', 'ignore')):
        return False
    return True
