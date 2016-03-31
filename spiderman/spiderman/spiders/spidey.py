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
from spiderman.items import MyItem


class fourthspider(scrapy.Spider):
    name = '4spider'
    allowed_domains = ['timesofindia.indiatimes.com']
    start_urls = [
        "http://timesofindia.indiatimes.com/"
    ]

    def __init__(self):
        if not os.path.exists("indexdir"):
            os.mkdir("indexdir")

        charmap = charset_table_to_dict(default_charset)
        my_analyzer = StemmingAnalyzer() | CharsetFilter(charmap)

        schema = Schema(url=ID(stored=True),
                        title=TEXT(stored=True),
                        content=TEXT(stored=True, analyzer=my_analyzer, spelling=True),
                        data=STORED,
                        tags=KEYWORD(stored=True),
                        urlid=STORED)

        self.ix = index.create_in("indexdir", schema)
        self.writer = self.ix.writer()
        self.logger.info("Writer created")
        self.regexp = [re.compile(r'www\.iitg\.ernet\.in'),
                       re.compile(r'iitg\.ernet\.in/news'),
                       re.compile(r'(&|\?)month=\d+'),
                       re.compile(r'(&|\?)year=\d+'),
                       re.compile(r'(&|\?)day=\d+'),
                       re.compile(r'http://iitg\.ernet\.in'),
                       re.compile(r'(((\?|&)sort=)|((\?|&)order=))'),
                       re.compile(r'/activities/all-events/(.)+'),
                       ]

        self.crawled_hash = []

    def close(self, spider, reason):
        self.logger.info("Commited Changes to indexing")
        self.writer.commit()
        return scrapy.Spider.close(spider, reason)

    def parse(self, response):

        soup = BeautifulSoup(response.selector.xpath('//html').extract()[0], 'html5lib')
        plain_text = soup.prettify()
        plain_text = plain_text.encode('ascii', 'ignore')
        m = hashlib.sha1(str(plain_text)).hexdigest()
        if str(m) not in self.crawled_hash:
            self.crawled_hash.append(str(m))
        else:
            return

        urls = []

        data = self.parse_data(response, m)

        item = MyItem()
        item['url'] = data['url']
        item['content'] = data['content']
        item['tags'] = data['tags']
        item['title'] = data['title']
        item['urlid'] = data['urlid']

        yield item

        for url in response.selector.xpath('//a/@href').extract():
            if url.endswith('#'):
                continue
            url = urlparse.urljoin(response.url, url.strip())
            if all((reg.search(url) is None) for reg in self.regexp):
                urls.append(url)

        for url in urls:
            self.logger.info('========== visiting url %s !!', url)
            yield scrapy.Request(url, callback=self.parse)

    def parse_data(self, response, m):

        soup = BeautifulSoup(response.selector.xpath('//html').extract()[0], 'html5lib')
        title = soup.title.string
        # content = soup.get_text()
        texts = soup.findAll(text=True)
        content = filter(visible, texts)

        tags = ""
        try:
            for h in soup.findAll(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7']):
                tags = tags + " " + h.string
        except:
            pass

        title = unicode(title)
        tags = unicode(tags)
        content = unicode(content)
        url = unicode(response.url)
        urlid = unicode(str(m))

        self.writer.add_document(url=url, title=title, data=content, content=content, tags=tags, urlid=urlid)
        self.logger.info("added To whoosh")
        return {'url': url, 'title': title, 'content': content, 'tags': tags, 'urlid': urlid}


def visible(element):
        if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
            return False
        elif re.match('<!--.*-->', element.encode('ascii', 'ignore')):
            return False
        return True
