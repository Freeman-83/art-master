from django.shortcuts import get_object_or_404

from djoser.views import UserViewSet

from rest_framework import pagination, permissions, viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from services.models import (Activity,
                             Favorite,
                             Service,
                             Review,
                             Tag)

from users.models import CustomUser, Subscribe

from .serializers import (ActivitySerializer,
                          CommentSerializer,
                          CustomUserSerializer,
                          ReviewSerializer,
                          ServiceSerializer,
                          TagSerializer)

from .permissions import IsAdminOrMasterOrReadOnly, IsAdminOrAuthorOrReadOnly

from .utils import create_relation, delete_relation


class CustomUserViewSet(UserViewSet):
    """Кастомный вьюсет для пользователей.
    (запрос на получение списка пользователей/пользователя
    настроен на получение профилей со статусом <мастер>)."""
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            return CustomUser.objects.filter(role='master')
        return super().get_queryset()

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=[permissions.IsAuthenticated, ])
    def subscribe(self, request, id):
        master = get_object_or_404(CustomUser, pk=id, role='master')
        if request.user != master:
            if request.method == 'POST':
                return create_relation(request,
                                       CustomUser,
                                       Subscribe,
                                       id,
                                       CustomUserSerializer,
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
            subscribers__user=request.user
        )
        page = self.paginate_queryset(subscribers_data)
        serializer = CustomUserSerializer(
            page, many=True, context={'request': request}
        )

        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для Тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для Активностей."""
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    pagination_class = None
    # filter_backends = (DjangoFilterBackend,)
    # filterset_class = IngredientFilterSet


class ServiceViewSet(viewsets.ModelViewSet):
    "Вьюсет для Сервисов."
    queryset = Service.objects.select_related(
        'master'
    ).prefetch_related(
        'tags', 'activities', 'locations'
    ).all()
    serializer_class = ServiceSerializer
    permission_classes = (IsAdminOrMasterOrReadOnly,)
    pagination_class = pagination.PageNumberPagination
    # filter_backends = (DjangoFilterBackend,)
    # filterset_class = RecipeFilterSet

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=[permissions.IsAuthenticated, ])
    def favorite(self, request, pk):
        if request.method == 'POST':
            return create_relation(request,
                                   Service,
                                   Favorite,
                                   pk,
                                   ServiceSerializer,
                                   field='service')
        return delete_relation(request,
                               Service,
                               Favorite,
                               pk,
                               field='service')


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для отзывов к Сервисам."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminOrAuthorOrReadOnly,)

    def get_queryset(self):
        service = get_object_or_404(Service, pk=self.kwargs.get('service_id'))
        return service.reviews.select_related('author').all()

    def perform_create(self, serializer):
        service = get_object_or_404(Service, pk=self.kwargs.get('service_id'))
        serializer.save(author=self.request.user, service=service)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментариев к отзывам."""
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