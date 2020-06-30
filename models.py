from django.db import models
from django.utils.timezone import now


class Comment(models.Model):
    text = models.CharField(max_length=200)
    article_id = models.CharField(max_length=200)
    pub_date = models.DateTimeField(default=now)
    up_votes = models.IntegerField(default=0)
    user_name = models.CharField(default="Guest", max_length=32)

    class Meta: 
        ordering = ('pub_date', )
