from django.shortcuts import render
from whoosh.qparser import QueryParser, FuzzyTermPlugin
from whoosh import index
import os


# Create your views here.

def searchview(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        ix = index.open_dir(os.path.join("..", "indexdir"))
        qp = QueryParser("content", schema=ix.schema)
        q = qp.parse(unicode(keyword))
        context = {}
        urls = []
        if 'page' not in request.GET:
            page = 1
        else:
            page = int(request.GET['page'])

        context['page'] = page

        with ix.searcher() as s:
            results = s.search_page(q, page)
            for hit in results:
                urls.append([hit['url'], hit['title'], hit['tags']])

            context['urls'] = urls
            context['nums'] = len(results)
            context['keyword'] = keyword

            corrected = s.correct_query(q, unicode(keyword))

        if corrected.query != q:
            context['dym'] = corrected.string
            qp.add_plugin(FuzzyTermPlugin())
            keyword_length = len(keyword)
            keyword_length /= 3
            q = qp.parse(unicode(keyword + '~/' + str(int(keyword_length))))
            with ix.searcher() as s:
                results = s.search_page(q, page)
                for hit in results:
                    urls.append([hit['url'], hit['title'], hit['tags']])

                context['urls'] = urls
                context['nums'] = len(results)

        return render(request, 'search.html', context)

    return render(request, 'search.html')
