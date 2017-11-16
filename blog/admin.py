from django.contrib import admin
from django.contrib.auth.models import User

from .models import Profile,Post,Comment,PostLike,CommentLike


def make_blogger(modeladmin, request, queryset):
    queryset.update(blogger=True)
make_blogger.short_description = "Mark selected blogger"

class ProfileAdmin(admin.ModelAdmin):

    list_display = ('user', 'blogger',  'request','notify',)
    list_filter = ('request','blogger',)
    search_fields = ['blogger', 'request']
    actions = [make_blogger]


class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'post',  'publish','archive',)

class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'comments',)


admin.site.register(Post,PostAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(CommentLike,CommentLikeAdmin)
admin.site.register(Comment)
admin.site.register(PostLike)