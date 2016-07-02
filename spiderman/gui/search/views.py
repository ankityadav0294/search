from django.shortcuts import render
from whoosh.qparser import QueryParser, FuzzyTermPlugin, MultifieldParser
from whoosh import index
import os
import re
import sqlite3
from django.http import HttpResponse


# Create your views here.

def searchview(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        ix = index.open_dir(os.path.join("..", "indexdir"))
        qp = MultifieldParser(["tags", "content", "title"], schema=ix.schema)
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
            if 'pdf' in request.GET and 'doc' in request.GET:
                results = s.search(q, limit=None)
                new_results = []
                for hit in results:
                    if hit['url'].endswith('.pdf') or hit['url'].endswith('.doc'):
                        new_results.append(hit)
                i = (page - 1) * 10
                while i < page * 10 and i < len(new_results):
                    hit = new_results[i]
                    i += 1
                    content = hit.highlights("content", top=8)
                    urls.append(
                            [hit['url'], hit['title'],
                             # tags.encode('utf-8', 'ignore'),
                             content.encode('utf-8', 'ignore')
                             ])

                context['urls'] = urls
                context['nums'] = len(new_results)
                context['keyword'] = keyword
                context['pdf'] = 'checked'
                context['doc'] = 'checked'

            elif 'doc' in request.GET:
                results = s.search(q, limit=None)
                new_results = []
                for hit in results:
                    if hit['url'].endswith('.doc'):
                        new_results.append(hit)
                i = (page - 1) * 10
                while i < page * 10 and i < len(new_results):
                    hit = new_results[i]
                    i += 1
                    content = hit.highlights("content", top=8)
                    urls.append(
                            [hit['url'], hit['title'],
                             # tags.encode('utf-8', 'ignore'),
                             content.encode('utf-8', 'ignore')
                             ])

                context['urls'] = urls
                context['nums'] = len(new_results)
                context['keyword'] = keyword
                context['doc'] = 'checked'

            elif 'pdf' in request.GET:
                results = s.search(q, limit=None)
                new_results = []
                for hit in results:
                    if hit['url'].endswith('.pdf'):
                        new_results.append(hit)
                i = (page - 1) * 10
                while i < page * 10 and i < len(new_results):
                    hit = new_results[i]
                    i += 1
                    content = hit.highlights("content", top=8)
                    urls.append(
                            [hit['url'], hit['title'],
                             # tags.encode('utf-8', 'ignore'),
                             content.encode('utf-8', 'ignore')
                             ])

                context['urls'] = urls
                context['nums'] = len(new_results)
                context['keyword'] = keyword
                context['pdf'] = 'checked'

            else:
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
                if 'pdf' in request.GET and 'doc' in request.GET:
                    results = s.search(q, limit=None)
                    new_results = []
                    for hit in results:
                        if hit['url'].endswith('.pdf') or hit['url'].endswith('.doc'):
                            new_results.append(hit)
                    i = (page - 1) * 10
                    while i < page * 10 and i < len(new_results):
                        hit = new_results[i]
                        i += 1
                        content = hit.highlights("content", top=8)
                        urls.append(
                                [hit['url'], hit['title'],
                                 # tags.encode('utf-8', 'ignore'),
                                 content.encode('utf-8', 'ignore')
                                 ])

                    context['urls'] = urls
                    context['nums'] = len(new_results)
                    context['keyword'] = keyword
                    context['pdf'] = 'checked'
                    context['doc'] = 'checked'

                elif 'doc' in request.GET:
                    results = s.search(q, limit=None)
                    new_results = []
                    for hit in results:
                        if hit['url'].endswith('.doc'):
                            new_results.append(hit)
                    i = (page - 1) * 10
                    while i < page * 10 and i < len(new_results):
                        hit = new_results[i]
                        i += 1
                        content = hit.highlights("content", top=8)
                        urls.append(
                                [hit['url'], hit['title'],
                                 # tags.encode('utf-8', 'ignore'),
                                 content.encode('utf-8', 'ignore')
                                 ])

                    context['urls'] = urls
                    context['nums'] = len(new_results)
                    context['keyword'] = keyword
                    context['doc'] = 'checked'

                elif 'pdf' in request.GET:
                    results = s.search(q, limit=None)
                    new_results = []
                    for hit in results:
                        if hit['url'].endswith('.pdf'):
                            new_results.append(hit)
                    i = (page - 1) * 10
                    while i < page * 10 and i < len(new_results):
                        hit = new_results[i]
                        i += 1
                        content = hit.highlights("content", top=8)
                        urls.append(
                                [hit['url'], hit['title'],
                                 # tags.encode('utf-8', 'ignore'),
                                 content.encode('utf-8', 'ignore')
                                 ])

                    context['urls'] = urls
                    context['nums'] = len(new_results)
                    context['keyword'] = keyword
                    context['pdf'] = 'checked'

                else:
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

        if context['nums'] % 10 == 0:
            context['end'] = context['nums'] / 10
        else:
            context['end'] = context['nums'] / 10 + 1
        if context['end'] < page:
            page = context['end']
        context['page'] = page
        return render(request, 'search.html', context)

    return render(request, 'search.html')


def autocomplete(request):
    if 'q' in request.GET:
        conn = sqlite3.connect(os.path.join("..", "words.db"))
        cursor = conn.cursor()
        sql = r"SELECT * FROM crawler WHERE word like '%s%%' LIMIT 6;" % request.GET['q']
        cursor.execute(sql)
        results = cursor.fetchall()
        xmlresponse = ''
        for i in results:
            xmlresponse += '<br><a href="?keyword=' + i[0] + '">' + i[0] + '</a>'
        return HttpResponse('%s' % xmlresponse)
