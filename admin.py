from django.contrib import admin
from .models import Post, PostImage, Comment, Subscriber, Newsletter, Image

admin.site.register(Image)

class PostImageAdmin(admin.StackedInline):
    model = PostImage

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'image', 'video', 'author', 'publish',
                    'status')
    list_filter = ('status', 'created_on', 'publish', 'author',)
    search_fields = ('title', 'body',)
    prepopulated_fields = {'slug': ('title', )}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')
    inlines = [PostImageAdmin]

    class Meta:
        model = Post
admin.site.register(Post, PostAdmin)

class PostImageAdmin(admin.ModelAdmin):
    pass
admin.site.register(PostImage, PostImageAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'body', 'post', 'created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('name', 'email', 'body')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)

admin.site.register(Comment, CommentAdmin)

def send_newsletter(modeladmin, request, queryset):
    for newsletter in queryset:
        newsletter.send(request)

send_newsletter.short_description = "Send selected Newsletters to all subscribers"


class NewsletterAdmin(admin.ModelAdmin):
    actions = [send_newsletter]

admin.site.register(Newsletter)
  
admin.site.register(Subscriber)
