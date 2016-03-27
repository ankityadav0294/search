import scrapy.spiders
import urlparse
from bs4 import BeautifulSoup
from whoosh.fields import Schema, TEXT, KEYWORD, ID
from whoosh.analysis import StemmingAnalyzer
import os, os.path
from whoosh import index
import re
from spiderman.items import MyItem


class fourthspider(scrapy.Spider):
    name = '4spider'
    allowed_domains = ['iitg.ernet.in']
    start_urls = [
        "http://intranet.iitg.ernet.in"
    ]

    def __init__(self):
        if not os.path.exists("indexdir"):
            os.mkdir("indexdir")

        schema = Schema(url=ID(stored=True),
                        title=TEXT(stored=True),
                        content=TEXT(analyzer=StemmingAnalyzer()),
                        tags=KEYWORD(stored=True),
                        data=TEXT(analyzer=StemmingAnalyzer()))

        self.ix = index.create_in("indexdir", schema)
        self.writer = self.ix.writer()
        self.logger.info("Writer created")

    def close(self, spider, reason):
        self.logger.info("Commited Changes to indexing")
        self.writer.commit()
        return scrapy.Spider.close(spider, reason)

    def parse(self, response):

        urls = []
        regexp = [re.compile(r'www\.iitg\.ernet\.in'),
                  re.compile(r'iitg\.ernet\.in/news'),
                  re.compile(r'(&|\?)month=\d+'),
                  re.compile(r'(&|\?)year=\d+'),
                  re.compile(r'http://iitg\.ernet\.in'),
                  re.compile(r'(((\?|&)sort=)|((\?|&)order=))'),
                  re.compile(r'/activities/all-events/(.)+'),
                  ]

        for url in response.xpath('//a/@href').extract():
            if url.endswith('#'):
                continue
            url = urlparse.urljoin(response.url, url.strip())
            if all((reg.search(url) is None) for reg in regexp):
                urls.append(url)

        data = self.parse_data(response)

        item = MyItem()
        item['url'] = data['url']
        item['content'] = data['content']
        item['data'] = data['data']
        item['tags'] = data['tags']
        item['title'] = data['title']
        yield item

        for url in urls:
            self.logger.info('========== visiting url %s !!', url)
            yield scrapy.Request(url, callback=self.parse)

    def parse_data(self, response):

        soup = BeautifulSoup(response.xpath('//html').extract()[0], 'html5lib')
        title = soup.title.string
        paras = ""
        headings = ""
        tables = ""

        try:
            for p in soup.body.p:
                paras = paras + " " + p
        except:
            pass
        try:
            for h in soup.findAll(['h1', 'h2', 'h3', 'h4', 'h5']):
                headings = headings + " " + h.string
        except:
            pass
        try:
            for td in soup.findAll('td'):
                tables = tables + " " + td.string
        except:
            pass

        paras += headings
        title = unicode(title)
        tables = unicode(tables)
        paras = unicode(paras)
        headings = unicode(headings)
        url = unicode(response.url)

        self.writer.add_document(url=url, title=title, content=paras, tags=headings, data=tables)
        self.logger.info("added To whoosh")
        return {'url': url, 'title': title, 'content': paras, 'tags': headings, 'data': tables}
