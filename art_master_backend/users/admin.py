from django.contrib import admin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'username',
                    'email',
                    'first_name',
                    'last_name',
                    'role',
                    'subscribers_count')
    list_display_links = ('username',)
    search_fields = ('username',)
    list_filter = ('username', 'email')
    empty_value_display = '-пусто-'

    def subscribers_count(self, master):
        return master.subscribers.all().count()
