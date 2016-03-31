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
        page  = 1
        if 'paginate' in request.GET:
            paginate = int(request.GET['paginate'])
            page = int(request.GET['page'])
            if paginate == 0:
                page -=1
            else:
                page +=1

        if page< 1:
                page = 1

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
        #
        # url_list = urls
        # paginator = Paginator(url_list, 10)
        # page = request.GET.get('page')
        # try:
        #     contacts = paginator.page(page)
        # except PageNotAnInteger:
        #     contacts = paginator.page(1)
        # except EmptyPage:
        #     contacts = paginator.page(paginator.num_pages)

        # context['urls'] = contacts
        if len(results)%10 == 0:
            context['end'] = len(results)/10
        else:
            context['end'] = len(results)/10 + 1
        if context['end'] < page:
            page =  context['end']
        context['page'] = page
        return render(request, 'search.html' , context)

    return render(request, 'search.html')
