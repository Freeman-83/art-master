from django.urls import include, path

from rest_framework import routers

from .views import (ActivityViewSet,
                    CommentViewSet,
                    ClientViewSet,
                    MasterViewSet,
                    ReviewViewSet,
                    ServiceViewSet)

app_name = 'api'

router = routers.DefaultRouter()

router.register('services', ServiceViewSet)
router.register('activities', ActivityViewSet)
router.register('users', ClientViewSet, basename='users')
router.register('masters', MasterViewSet, basename='masters')
router.register(
    r'services/(?P<service_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'services/(?P<service_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('', include(router.urls)),
    # path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
