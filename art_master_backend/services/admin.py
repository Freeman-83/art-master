from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from .models import (Activity,
                     ActivityService,
                     Comment,
                     Location,
                     LocationService,
                     Review,
                     Service)


class ActivityInService(admin.TabularInline):
    model = ActivityService
    min_num = 1


class LocationInService(admin.TabularInline):
    model = LocationService
    min_num = 1


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    empty_value_display = '-пусто-'


@admin.register(Location)
class LocationAdmin(OSMGeoAdmin):
    list_display = ('id',
                    'address',
                    'point')
    list_display_links = ('address',)
    search_fields = ('address',)
    list_filter = ('address',)
    empty_value_display = '-пусто-'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'name',
                    'master',
                    'created',
                    'additions_in_favorite_count')
    list_display_links = ('name',)
    search_fields = ('name', 'master')
    list_filter = ('name', 'master')
    empty_value_display = '-пусто-'

    inlines = [ActivityInService, LocationInService]

    @admin.display(description='Количество добавлений в избранное')
    def additions_in_favorite_count(self, service):
        return service.in_favorite_for_clients.all().count()


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'author', 'score')
    list_display_links = ('service',)
    search_fields = ('service', 'author')
    list_filter = ('service', 'author')
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'review', 'author')
    list_display_links = ('review',)
    search_fields = ('review', 'author')
    list_filter = ('review', 'author')
    empty_value_display = '-пусто-'


@admin.register(ActivityService)
class ActivityServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'activity', 'service')
    search_fields = ('activity', 'service')
    list_filter = ('activity', 'service')
    empty_value_display = '-пусто-'


@admin.register(LocationService)
class LocationServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'location', 'service')
    search_fields = ('location', 'service')
    list_filter = ('location', 'service')
    empty_value_display = '-пусто-'
