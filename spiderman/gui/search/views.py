from django.shortcuts import render
from whoosh.qparser import QueryParser, FuzzyTermPlugin
from whoosh import index
import os
import re


# Create your views here.

def searchview(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        ix = index.open_dir(os.path.join("..", "indexdir"))
        qp = QueryParser("content", schema=ix.schema)
        q = qp.parse(unicode(keyword))
        context = {}
        urls = []
        page = 1
        if 'paginate' in request.GET:
            paginate = int(request.GET['paginate'])
            page = int(request.GET['page'])
            if paginate == 0:
                page -= 1
            else:
                page += 1

        if page < 1:
            page = 1

        with ix.searcher() as s:
            results = s.search_page(q, page)
            for hit in results:
                content = hit.highlights("content", top=8)
                # content = re.sub('((\'|\"), u(\'|\"))', '... ', content)
                # content = re.sub('(\\\u)|(\'u)|(u\')|(\|)|(\\\\)', '', content)
                # tags = hit.highlights("tags", top=4)
                # tags = re.sub('((\'|\"), u(\'|\"))', '... ', tags)
                # tags = re.sub('(\\\u)|(\'u)|(u\')|(\|)|(\\\\)', '', tags)
                urls.append(
                        [hit['url'], hit['title'],
                         # tags.encode('utf-8', 'ignore'),
                         content.encode('utf-8', 'ignore')
                         ])

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
                    content = hit.highlights("content", top=8)
                    content = re.sub('((\'|\"), u(\'|\"))', '... ', content)
                    content = re.sub('(\\\u)|(\'u)|(u\')|(\|)|(\\\\)', '', content)
                    tags = hit.highlights("tags", top=4)
                    tags = re.sub('((\'|\"), u(\'|\"))', '... ', tags)
                    tags = re.sub('(\\\u)|(\'u)|(u\')|(\|)|(\\\\)', '', tags)
                    urls.append([hit['url'], hit['title'], tags.encode('utf-8', 'ignore'),
                                 content.encode('utf-8', 'ignore')])

                context['urls'] = urls
                context['nums'] = len(results)

        if len(results) % 10 == 0:
            context['end'] = len(results) / 10
        else:
            context['end'] = len(results) / 10 + 1
        if context['end'] < page:
            page = context['end']
        context['page'] = page
        return render(request, 'search.html', context)

    return render(request, 'search.html')
