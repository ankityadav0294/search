import scrapy.spiders
import urlparse
from bs4 import BeautifulSoup
from whoosh.fields import Schema, TEXT, KEYWORD, ID
from whoosh.analysis import StemmingAnalyzer, CharsetFilter
from whoosh.support.charset import default_charset, charset_table_to_dict

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
                        content=TEXT(analyzer=my_analyzer, stored=True),
                        tags=KEYWORD(stored=True))

        self.ix = index.create_in("indexdir", schema)
        self.writer = self.ix.writer()
        self.logger.info("Writer created")
        self.regexp = [re.compile(r'www\.iitg\.ernet\.in'),
                       re.compile(r'iitg\.ernet\.in/news'),
                       re.compile(r'(&|\?)month=\d+'),
                       re.compile(r'(&|\?)year=\d+'),
                       re.compile(r'http://iitg\.ernet\.in'),
                       re.compile(r'(((\?|&)sort=)|((\?|&)order=))'),
                       re.compile(r'/activities/all-events/(.)+'),
                       ]

    def close(self, spider, reason):
        self.logger.info("Commited Changes to indexing")
        self.writer.commit()
        return scrapy.Spider.close(spider, reason)

    def parse(self, response):

        urls = []

        data = self.parse_data(response)

        item = MyItem()
        item['url'] = data['url']
        item['content'] = data['content']
        item['tags'] = data['tags']
        item['title'] = data['title']
        yield item

        for url in response.xpath('//a/@href').extract():
            if url.endswith('#'):
                continue
            url = urlparse.urljoin(response.url, url.strip())
            if all((reg.search(url) is None) for reg in self.regexp):
                urls.append(url)

        for url in urls:
            self.logger.info('========== visiting url %s !!', url)
            yield scrapy.Request(url, callback=self.parse)

    def parse_data(self, response):

        soup = BeautifulSoup(response.xpath('//html').extract()[0], 'html5lib')
        title = soup.title.string
        content = soup.get_text()
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

        self.writer.add_document(url=url, title=title, content=content, tags=tags)
        self.logger.info("added To whoosh")
        return {'url': url, 'title': title, 'content': content, 'tags': tags}
