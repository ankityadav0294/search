from django.shortcuts import render
from whoosh.qparser import QueryParser
from whoosh import index
import os
# Create your views here.

def searchview(request):
    if request.method == 'POST':
        keyword = request.POST['keyword']
        ix = index.open_dir(os.path.join("..","indexdir"))
        qp = QueryParser("content", schema=ix.schema)
        q = qp.parse(keyword)
        with ix.searcher() as s:
            results = s.search(q)
        keyword = []
        for hit in results:
            keyword.append(hit['url'], hit['title'])
        return render(request, 'search.html', {'keyword': keyword})
    return render(request, 'search.html', {'keyword': ""})