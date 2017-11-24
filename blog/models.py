from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from ckeditor.fields import RichTextField
from django.template.defaultfilters import slugify
from django.urls import reverse


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    blogger = models.BooleanField(default=False)
    request = models.BooleanField(default=False)
    notify =  models.BooleanField(default=False)
    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Post(models.Model):
    user = models.ForeignKey(User,null=True,blank=True, on_delete=models.CASCADE)
    post = models.CharField(max_length=100,verbose_name='Title',unique=True)
    likes = models.IntegerField(default=0)
    description = RichTextField(verbose_name='Description')
    publish = models.BooleanField(default=False,verbose_name='Publish')
    published = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(default=timezone.now)
    archive = models.BooleanField(default=False)
    archive_date = models.DateTimeField(null=True,blank=True)
    views = models.IntegerField(default=0)
    slug = models.SlugField(blank=True)
  

    def __str__(self):
        return self.post

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.post) #Or whatever you want the slug to use
        super(Post, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:viewpost', kwargs = {'slug' : self.slug})


class Comment(models.Model):
    posts = models.ForeignKey(Post,null=True,blank=True, on_delete=models.CASCADE)
    comment = models.CharField(max_length=100)
    author = models.ForeignKey(User, null=True, blank=True)
    likes = models.IntegerField(default=0)
    notifications = models.CharField(max_length=50,blank=True)
    com_created = models.DateTimeField(auto_now=True)
    approve = models.BooleanField(default=True)

    def __str__(self):
        return self.comment

    class Meta:
        ordering = ['-com_created']

class PostLike(models.Model):
    posts = models.ForeignKey(Post,null=True,blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True)
    ip = models.CharField(max_length=20)

class CommentLike(models.Model):
    comments = models.ForeignKey(Comment,null=True,blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True)
    ip = models.CharField(max_length=20)

class Search(models.Model):
    search = models.CharField(max_length=30)

