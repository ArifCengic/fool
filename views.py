from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .models import Comment
from .form import CommentForm
from django.http import Http404
from random import randint
import json
import datetime as dt
from django.conf import settings
import redis

# time stamp string format in input JSON in Redis
TS_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

# Connect to Redis instance
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                   port=settings.REDIS_PORT,
                                   db=0)


def convert_str_date(dic, key):
    """Convert date string to datetime for use in Django Views."""
    if key in dic and type(d[key]) == str:
        dic[key] = dt.datetime.strptime(dic[key], TS_FORMAT)


def get_random_list(arr, count):
    """Get count number of random and unique elements from arr list."""
    total = redis_instance.llen(arr)
    random_indexes = []

    while len(random_indexes) < count:
        value = randint(0, total-1)
        if value not in random_indexes:
            random_indexes.append(value)

    result = []

    for i in random_indexes:
        # get string val from Redis list convert to JSON
        value = redis_instance.lrange(arr, i, i)[0]
        a = json.loads(value.decode('utf-8'))
        convert_str_date(a, 'publish_at')
        result.append(a)
  
    return result


def article(request, article_id):
    """Article page with article with uuid, and list of 3 quotes."""
    if request.method == 'POST':
        cf = CommentForm(request.POST)
        if cf.is_valid():
            c = Comment(text=cf.cleaned_data['text'],
                        article_id=article_id)
            c.save()
            return HttpResponseRedirect(request.path_info)
        else:
            # TODO check for faul language, curse words etc in comment text
            return HttpResponse(f"Problem with your comment {cf.cleaned_data['text']} on Article ID {article_id}.")

    try:
        value = redis_instance.hget('ArticlesHash', article_id)
        article = json.loads(value)
        convert_str_date(article, 'publish_at')
    except Exception:
        raise Http404(f"Can not find Article {article_id} .")

    try:
        quotes = get_random_list("QuotesList", 3)
    except Exception:
        raise Http404("Can not find stock Quotes.")

    comments = Comment.objects.filter(article_id=article_id)

    return render(request, 'articles/article.html', {
        'stocks': quotes,
        'article': article,
        'comments': comments,
        'form': CommentForm()
    })


def home(request):
    """Home page with 4 random selected articles, top one w slug=10-promise."""
    try:
        top_article = get_random_list("ArticlesPromiseList", 1)[0]
    except Exception:
        raise Http404("Can not find top article with slug 10-promise.")
  
    try:
        other_articles = get_random_list("ArticlesList", 3)
    except Exception:
        raise Http404("Can not find top article with slug 10-promise.")

    return render(request, 'articles/home.html', {
                    'top': top_article,
                    'articles': other_articles
                })


def vote(request):
    """Ajax call to add an up vote to comment comment_pk."""
    comment_pk = request.GET.get('comment_pk')
    c = Comment.objects.get(pk=int(comment_pk))
    c.up_votes += 1
    c.save()

    return JsonResponse({'id': comment_pk, 'count': c.up_votes})
