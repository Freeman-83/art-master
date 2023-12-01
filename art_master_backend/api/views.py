from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from djoser.conf import settings
from djoser.views import UserViewSet

from rest_framework import permissions, viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import ActivityFilterSet, ServiceFilterSet

from services.models import (Activity,
                             Favorite,
                             Location,
                             Service,
                             Review,
                             Tag)

from .permissions import IsAdminOrMasterOrReadOnly, IsAdminOrAuthorOrReadOnly

from .serializers import (ActivitySerializer,
                          CommentSerializer,
                          LocationSerializer,
                          MasterContextSerializer,
                          ReviewSerializer,
                          ServiceSerializer,
                          ServiceContextSerializer,
                          TagSerializer)

from users.models import CustomUser, Subscribe

from .utils import create_relation, delete_relation


class CustomUserViewSet(UserViewSet):
    """Кастомный базовый вьюсет всех пользователей."""

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [permissions.IsAuthenticated, ]
        return super().get_permissions()


class MasterViewSet(CustomUserViewSet):
    """Кастомный вьюсет Мастера."""

    def get_permissions(self):
        if self.action == 'retrieve':
            self.permission_classes = settings.PERMISSIONS.master
        return super().get_permissions()

    def get_queryset(self):
        return CustomUser.objects.filter(is_master=True)

    def get_serializer_class(self):
        if self.action == "create":
            if settings.USER_CREATE_PASSWORD_RETYPE:
                return settings.SERIALIZERS.user_create_password_retype
            return settings.SERIALIZERS.master_create
        if self.action in ['list', 'retrieve']:
            return settings.SERIALIZERS.master
        return super().get_serializer_class()


class ClientViewSet(CustomUserViewSet):
    """Кастомный вьюсет Клиента."""

    def get_queryset(self):
        if self.action == 'list' and not self.request.user.is_staff:
            return CustomUser.objects.filter(is_master=True)
        return CustomUser.objects.filter(is_master=False)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=[permissions.IsAuthenticated, ])
    def subscribe(self, request, id):
        master = get_object_or_404(CustomUser, pk=id, is_master=True)
        if request.user != master:
            if request.method == 'POST':
                return create_relation(request,
                                       CustomUser,
                                       Subscribe,
                                       id,
                                       MasterContextSerializer,
                                       field='master')
            return delete_relation(request,
                                   CustomUser,
                                   Subscribe,
                                   id,
                                   field='master')
        return Response(
            data={'errors': 'Подписка на самого себя запрещена'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False,
            permission_classes=[permissions.IsAuthenticated, ])
    def subscriptions(self, request):
        subscribers_data = CustomUser.objects.filter(
            subscribers__client=request.user
        )
        page = self.paginate_queryset(subscribers_data)
        serializer = MasterContextSerializer(
            page, many=True, context={'request': request}
        )

        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет Тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет Активностей."""
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ActivityFilterSet


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    """Вьюсет Сервисов."""
    queryset = Service.objects.select_related(
        'master'
    ).prefetch_related(
        'tags', 'activities', 'locations'
    ).annotate(
        rating=Avg('reviews__score')
    ).all()
    serializer_class = ServiceSerializer
    permission_classes = (IsAdminOrMasterOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ServiceFilterSet

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=[permissions.IsAuthenticated, ])
    def favorite(self, request, pk):
        if request.method == 'POST':
            return create_relation(request,
                                   Service,
                                   Favorite,
                                   pk,
                                   ServiceContextSerializer,
                                   field='service')
        return delete_relation(request,
                               Service,
                               Favorite,
                               pk,
                               field='service')


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет Отзывов к Сервисам."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminOrAuthorOrReadOnly,)

    def get_queryset(self):
        service = get_object_or_404(Service, pk=self.kwargs.get('service_id'))
        return service.reviews.select_related('author').all()

    def perform_create(self, serializer):
        service = get_object_or_404(Service, pk=self.kwargs.get('service_id'))
        serializer.save(author=self.request.user, service=service)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет Комментариев к Отзывам."""
    serializer_class = CommentSerializer
    permission_classes = (IsAdminOrAuthorOrReadOnly,)

    def get_queryset(self):
        service = get_object_or_404(Service, pk=self.kwargs.get('service_id'))
        review = service.reviews.get(pk=self.kwargs.get('review_id'))
        return review.comments.select_related('author').all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            service=self.kwargs.get('service_id')
        )
        serializer.save(author=self.request.user, review=review)
