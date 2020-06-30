from django.core.management.base import BaseCommand, CommandError
import json
from django.conf import settings
import redis


class Command(BaseCommand):
    """Adding populate_redis command to manage.py ."""

    help = 'Imports data for Articles and Quotes from JSON files'

    # TODO add 2 arguments to pass in file-names
    # def add_arguments(self, parser):
    #     parser.add_argument('content_api', nargs='+', type=str)

    def handle(self, *args, **options):
        """Import data to from JSON files into Redis."""
        redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                           port=settings.REDIS_PORT, 
                                           db=0)

        redis_instance.flushdb()

        with open('content_api.json',) as f:
            data = json.load(f)
            articles = data['results']
            for i, a in enumerate(articles):

                if (redis_instance.llen('ArticlesList') < 10):
                    # we use Redis list to store values for index based random selection
                    # and Redis hash to lookup Articles by 'uuid' - assuming its unique
                    redis_instance.lpush('ArticlesList', json.dumps(a))
                    redis_instance.hset('ArticlesHash', a['uuid'], json.dumps(a))
                   
                    print(f" {i} - {a['headline']}  {a['uuid']}")

                    for t in a['tags']:
                        if t['slug'] == "10-promise":
                            redis_instance.lpush('ArticlesPromiseList', json.dumps(a))

        with open('quotes_api.json',) as f:
            quotes = json.load(f)
            if (redis_instance.llen('QuotesList') < 25):
                print(f"Adding {len(quotes)} Quotes to Redis")
                for q in quotes:
                    redis_instance.lpush('QuotesList', json.dumps(q))

        redis_instance.bgsave()
        self.stdout.write(self.style.SUCCESS('Successfully populated Redis'))