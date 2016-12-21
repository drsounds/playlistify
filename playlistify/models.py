import datetime

from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

class SpotifySession(models.Model):
    access_token = models.CharField(max_length=255)
    user = models.OneToOneField(User)
    refresh_token = models.CharField(max_length=255)
    issued = models.DateTimeField(default=datetime.datetime.now)
    expires_in = models.IntegerField()
    username = models.CharField(max_length=255)


class Category(models.Model):
    slug = models.SlugField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField()
    icon = models.CharField(max_length=25)
    
    def save(self, *args, **kwargs):
        if not self.id:
            # Newly created object, so set slug
            self.s = slugify(self.name)

        super(Category, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    

class Playlist(models.Model):
    slug = models.SlugField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField()
    uri = models.CharField(max_length=255)
    tags = models.TextField()
    categories = models.ManyToManyField(Category)
    user = models.ForeignKey(User)
    
    def save(self, *args, **kwargs):
        if not self.id:
            # Newly created object, so set slug
            self.s = slugify(self.name)

        super(Playlist, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name
