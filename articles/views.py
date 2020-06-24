from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Comment
from .form import CommentForm
from django.http import Http404
from random import randint
import json, os, datetime
from django.conf import settings
import redis

# Connect to our Redis instance
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                   port=settings.REDIS_PORT, db=0)

articles = []
articles_promise_slug = []
with open('content_api.json',) as f:
    data = json.load(f)
    articles = data['results']
    for i, a in enumerate(articles):
        print(f" {i} - {a['headline']}")
        # Convert string publish_at to datetime so it can be easily formated
        # if type(a['publish_at']) == str:
        #     a['publish_at'] = datetime.datetime.strptime(
        #                         a['publish_at'],
        #                         "%Y-%m-%dT%H:%M:%S%z")

        if (redis_instance.llen('ArticlesList') < 10):
            redis_instance.lpush('ArticlesList', json.dumps(a))

            for t in a['tags']:
                if t['slug'] == "10-promise":
                    redis_instance.lpush('ArticlesPromiseList', json.dumps(a))
                # articles_promise_slug.append(a)

quotes = []
with open('quotes_api.json',) as f:
    quotes = json.load(f)
    if (redis_instance.llen('QuotesList') < 25):
        print(f"Adding {len(quotes)} Quotes to Redis")
        for q in quotes:
            redis_instance.lpush('QuotesList', json.dumps(q))



def get_random_list(arr, count):

    total = redis_instance.llen(arr)
    # if (len(arr) == 0 or count > len(arr)):
    #     return []

    random_indexes = []

    while len(random_indexes) < count:
        value = randint(0, total-1)
        if value not in random_indexes:
            random_indexes.append(value)

    result = []
    
    for i in random_indexes:
        value = redis_instance.lrange(arr,i,i)[0]
        a = json.loads(value.decode('utf-8'))

        # For ArticlesList Convert string publish_at to datetime 
        # so it can be easily formated in Django Views
        if arr == "ArticlesList" and type(a['publish_at']) == str:
            a['publish_at'] = datetime.datetime.strptime(
                                a['publish_at'],
                                "%Y-%m-%dT%H:%M:%S%z")
        result.append(a)
    
    return result


def article(request, article_id):

    if request.method == 'POST':
        cf = CommentForm(request.POST)
        if cf.is_valid():
            c = Comment(text=cf.cleaned_data['text'],
                        article_id=article_id)
            c.save()
        else:
            return HttpResponse(f"Got your comment {cf.cleaned_data['text']} on Article ID {article_id}.")

    try:
        article = next(a for a in articles if a['uuid'] == article_id)
    except StopIteration:
        raise Http404(f"Can not find Article {article_id}")

    comments = Comment.objects.filter(article_id=article_id).order_by('pub_date')

    return render(request, 'articles/article.html', {
        # 'stocks': get_random_list(quotes, 3),
        'stocks': get_random_list("QuotesList", 3),
        'article': article,
        'comments': comments,
        'form': CommentForm()
    })


def home(request):

    try:
        top_article = get_random_list("ArticlesPromiseList", 1)[0]
    except IndexError:
        raise Http404("Can not find top article with slug 10-promise")

    other_articles = get_random_list("ArticlesList", 3)

    return render(request, 'articles/home.html', {
        "top": top_article,
        'articles': other_articles
    })


def vote(request):

    comment_pk = request.GET.get('comment_pk')
    c = Comment.objects.get(pk=int(comment_pk))
    c.up_votes += 1
    c.save()

    return JsonResponse({'id': comment_pk, 'count': c.up_votes})
