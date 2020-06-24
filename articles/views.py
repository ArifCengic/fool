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

        if (redis_instance.llen('ArticlesList') < 10):
            # we use Redis list to store values for index based random selection
            # and Redis hash to lookup Articles by 'uuid' - assuming its unique i
            # TODO replace redis list with hash (key-value) and set
            # use SRANDMEMBER key [count] to get count random keys 
            # redis_instance.sadd("QuotesSet", json.dumps(q))
            redis_instance.lpush('ArticlesList', json.dumps(a))
            redis_instance.hset('ArticlesHash', a['uuid'], json.dumps(a))

            for t in a['tags']:
                if t['slug'] == "10-promise":
                    redis_instance.lpush('ArticlesPromiseList', json.dumps(a))
                

quotes = []
with open('quotes_api.json',) as f:
    quotes = json.load(f)
    if (redis_instance.llen('QuotesList') < 25):
        print(f"Adding {len(quotes)} Quotes to Redis")
        for q in quotes:
            redis_instance.lpush('QuotesList', json.dumps(q))
            
def convert_str_date(a, key):
    # For Articles need to convert date string to datetime 
    # so it can be formated as date and time in Django Views
    if key in a and type(a[key]) == str:
            a[key] = datetime.datetime.strptime(
                                a[key],
                                "%Y-%m-%dT%H:%M:%S%z")

def get_random_list(arr, count):

    total = redis_instance.llen(arr)
    random_indexes = []

    while len(random_indexes) < count:
        value = randint(0, total-1)
        if value not in random_indexes:
            random_indexes.append(value)

    result = []
    
    for i in random_indexes:
        # get string val from Redis list convert to JSON
        value = redis_instance.lrange(arr,i,i)[0]
        a = json.loads(value.decode('utf-8'))
        convert_str_date(a, 'publish_at')
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
            #TODO check fo faul language, curse words etc in comment text
            return HttpResponse(f"Problem with your comment {cf.cleaned_data['text']} on Article ID {article_id}.")

    try:
        value = redis_instance.hget('ArticlesHash', article_id)
        article = json.loads(value)
        convert_str_date(article, 'publish_at')
    except:
        raise Http404(f"Can not find Article {article_id}")

    comments = Comment.objects.filter(article_id=article_id).order_by('pub_date')

    return render(request, 'articles/article.html', {
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
