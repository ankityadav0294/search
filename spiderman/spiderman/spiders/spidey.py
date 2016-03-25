import scrapy.spiders
import urlparse
from bs4 import BeautifulSoup
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.analysis import StemmingAnalyzer
import os, os.path
from whoosh import index
import re
from spiderman.items import MyItem

class fourthspider(scrapy.Spider):
    name = '4spider'
    allowed_domains = ['doc.scrapy.org']
    start_urls = [
        "http://doc.scrapy.org/en/latest/"
    ]

    def parse(self, response):

        urls = []
        regexp = [re.compile(r'www\.iitg\.ernet\.in'),
                  re.compile(r'iitg\.ernet\.in\/news\/node'),
                  re.compile(r'(&|\?)month=\d+'),
                  re.compile(r'(&|\?)year=\d+'),
                  re.compile(r'http\:\/\/iitg\.ernet\.in'),
                  re.compile(r'(((\?|&)sort=)|((\?|&)order=))'),
                  re.compile(r'\/activities\/all-events\/(.)+'),
                  ]

        for url in response.xpath('//a/@href').extract():
            if url.endswith('#'):
                continue
            url = urlparse.urljoin(response.url, url.strip())
            if all((reg.search(url) is None) for reg in regexp):
                urls.append(url)

        self.parse_data(response)

        item = MyItem()
        item['url'] = response.url
        yield item

        for url in urls:
            self.logger.info('========== visiting url %s !!', url)
            yield scrapy.Request(url, callback=self.parse)

    @staticmethod
    def parse_data(response):

        soup = BeautifulSoup(response.xpath('//html').extract()[0], 'html5lib')
        title = response.xpath('//title').extract()[0]
        paras = ""
        headings = ""
        tables = ""

        for p in soup.findAll('p'):
            try:
                paras = paras + p.string
            except:
                pass

        for h in soup.findAll(['h1', 'h2', 'h3', 'h4', 'h5']):
            try:
                headings = headings + h.string
            except:
                pass

        for td in soup.findAll('td'):
            try:
                tables = tables + td.string
            except:
                pass

        title = unicode(title)
        tables = unicode(tables)
        paras = unicode(paras)
        headings = unicode(headings)
        url = unicode(response.url)

        schema = Schema(url=ID(stored=True),
                        title=TEXT(stored=True),
                        content=TEXT(analyzer=StemmingAnalyzer()),
                        tags=KEYWORD(stored=True),
                        data=TEXT(analyzer=StemmingAnalyzer()))

        if not os.path.exists("indexdir"):
            os.mkdir("indexdir")

        ix = index.create_in("indexdir", schema)

        writer = ix.writer()
        writer.add_document(url=url, title=title, content=paras, tags=headings, data=tables)
        writer.commit()
