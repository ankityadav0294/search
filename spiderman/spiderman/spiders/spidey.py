import scrapy.spiders
import urlparse
from bs4 import BeautifulSoup
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.analysis import StemmingAnalyzer
import os, os.path
from whoosh import index
from whoosh.qparser import QueryParser
import re

class fourthspider(scrapy.Spider):
    name = '4spider'
    allowed_domains = ['iitg.ernet.in']
    start_urls = [
        "http://intranet.iitg.ernet.in/"
    ]
    def parse(self, response):

        soup = BeautifulSoup(response.xpath('//html').extract()[0], 'html5lib')
        urls = []
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
        yield {'url':url, 'title':title, 'content':paras, 'tags':headings, 'data':tables}
        for url in response.xpath('//a/@href').extract():
            if '#' in url:
                continue
	    regexp1 = re.compile(r'[^www].(iitg\.ernet\.in)')
	    regexp2 = re.compile(r'(iitg\.ernet\.in).[^/news/node/]')
	    if regexp1.search(url) is not None:
		if regexp2.search(url) is not None:
	            url = urlparse.urljoin(response.url, url.strip())
        	    urls.append(url)

        for url in urls:
            self.logger.info('========== visiting url %s !!', url)
            yield scrapy.Request(url, callback=self.parse)
