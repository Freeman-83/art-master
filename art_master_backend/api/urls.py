from django.urls import include, path

from rest_framework import routers

from .views import (ActivityViewSet,
                    CommentViewSet,
                    CustomUserViewSet,
                    ReviewViewSet,
                    ServiceViewSet,
                    TagViewSet)

app_name = 'api'

router = routers.DefaultRouter()

router.register('services', ServiceViewSet)
router.register('activities', ActivityViewSet)
router.register('tags', TagViewSet)
router.register('users', CustomUserViewSet)
# router.register('masters', CustomUserViewSet)
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
