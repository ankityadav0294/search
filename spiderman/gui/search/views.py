from django.shortcuts import render
from whoosh.qparser import QueryParser
from whoosh import index
import os


# Create your views here.

def searchview(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        ix = index.open_dir(os.path.join("..", "indexdir"))
        qp = QueryParser("content", schema=ix.schema)
        q = qp.parse(unicode(keyword))
        urls = {}
        titles = {}
        with ix.searcher() as s:
            results = s.search(q)
            i = 0
            for hit in results:
                urls[i] = hit['url']
                titles[i] = hit['title']
                i += 1
            context = {'urls': urls, 'titles': titles, 'nums': len(results)}
        return render(request, 'search.html', context)
    return render(request, 'search.html', {'urls': ['NULL'], 'titles': ['NULL'], 'nums': -1})
