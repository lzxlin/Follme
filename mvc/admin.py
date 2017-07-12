from django.contrib import admin
from models import *
# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name')
    list_display_links = ('id','name')
    list_per_page = ADMIN_PAGE_SIZE

class AreaAdmin(admin.ModelAdmin):
    list_display = ('id','name','code')
    list_display_links = ('id','name','code')
    list_per_page = ADMIN_PAGE_SIZE

class UserAdmin(admin.ModelAdmin):
    list_display = ('id','username','realname','email','addtime_format')
    list_display_links = ('username','realname','email')
    list_per_page = ADMIN_PAGE_SIZE

class NoteAdmin(admin.ModelAdmin):
    list_display = ('id','user_name','message_short','addtime_format_admin','category_name')
    list_display_links = ('id','message_short')
    search_fields = ['message']
    list_per_page = ADMIN_PAGE_SIZE

class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_name', 'content', 'pub_time_format_admin')
    list_display_links = ('id', 'content')
    search_fields = ['content']
    list_per_page = ADMIN_PAGE_SIZE

class PollNoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_name', 'note_content', 'ifpoll')
    #list_display_links = ('id', 'content')

class ThreadNoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_name', 'note_content', 'ifthread')
    #list_display_links = ('id', 'content')

class ThreadCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_name', 'ifthread')
    #list_display_links = ('id', 'content')

class PollCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_name', 'ifpoll')
    #list_display_links = ('id', 'content')


admin.site.register(Note, NoteAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(User,UserAdmin)
admin.site.register(Area,AreaAdmin)
admin.site.register(PollComment,PollCommentAdmin)
admin.site.register(PollNote,PollNoteAdmin)
admin.site.register(TheadComment,ThreadCommentAdmin)
admin.site.register(ThreadNote,ThreadNoteAdmin)
admin.site.register(Message)
admin.site.register(Notice)
admin.site.register(Article)
admin.site.register(ArticleType)
admin.site.register(Notice_like)
admin.site.register(Notice_tread)
admin.site.register(Notice_poll)
admin.site.register(Notice_friend)

