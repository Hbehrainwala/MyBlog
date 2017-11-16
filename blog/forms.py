from django import forms
from blog.models import Post,Comment,Profile,Search
from django.contrib.auth.models import User

from django.utils import timezone
from ckeditor.fields import RichTextField
from datetimewidget.widgets import DateTimeWidget


class CreatePostForm(forms.ModelForm):
  # published = forms.DateTimeField(widget=DateTimeWidget( bootstrap_version=3),initial=timezone.now)
  class Meta:
    model = Post
    fields = ('post','description', 'publish', 'published',)

    
class UpdateUserForm(forms.ModelForm):
  class Meta:
    model = User
    fields = ('first_name','last_name','email')

class UpdatePostForm(forms.ModelForm):
  class Meta:
    model = Post
    fields = ('post','description','publish')

class CommentForm(forms.ModelForm):
  class Meta:
    model = Comment
    fields = ('comment',)

class NotificationForm(forms.ModelForm):
  class Meta:
    model = Profile
    fields = ('notify',)

class SearchForm(forms.ModelForm):
  class Meta:
    model = Search
    fields = ('search',)
