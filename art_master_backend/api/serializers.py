import webcolors

from django.shortcuts import get_object_or_404

from drf_extra_fields.fields import Base64ImageField

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from djoser.serializers import UserSerializer, UserCreateSerializer

from .utils import get_validated_field

from services.models import (Activity,
                             Comment,
                             Location,
                             Review,
                             Service,
                             Tag)

from users.models import CustomUser


class Hex2NameColor(serializers.Field):
    """Кастомное поле для преобразования цветового кода."""

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class ServiceContextSerializer(serializers.ModelSerializer):
    "Сериализатор для отображения профиля рецепта в других контекстах."
    activities = serializers.StringRelatedField(many=True)

    class Meta:
        model = Service
        fields = ('id',
                  'name',
                  'activities')


class RegisterUserSerializer(UserCreateSerializer):
    """Кастомный базовый сериализатор для регистрации пользователя."""

    class Meta:
        model = CustomUser
        fields = ('id',
                  'username',
                  'email',
                  'first_name',
                  'last_name',
                  'password',
                  'role',
                  'bio',
                  'foto',
                  'phone_number')

    # def __init__(self, instance=None, data=..., **kwargs):
    #     if self.Meta.fields['role'] == 'master':
    #         super().__init__()
    #     super().__init__(instance, data, **kwargs)

    def get_extra_kwargs(self):
        role = self.initial_data.get('role')
        value = {'required': True} if role == 'master' else {'write_only': True}
        kwargs = {'bio': value,
                  'foto': value,
                  'phone_number': value}

        return kwargs


class CustomUserSerializer(UserSerializer):
    """Кастомный сериализатор для пользователей."""
    services = ServiceContextSerializer(many=True, read_only=True)
    subscribers_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id',
                  'username',
                  'email',
                  'first_name',
                  'last_name',
                  'role',
                  'services',
                  'subscribers_count',
                  'is_subscribed')

    def get_is_subscribed(self, master):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.subscriptions.filter(master=master).exists()

    def get_subscribers_count(self, master):
        return master.subscribers.all().count()


class CustomUserContextSerializer(UserSerializer):
    """ Кастомный сериализатор для отображения профиля пользователя
    в других контекстах."""
    is_subscribed = serializers.SerializerMethodField()
    subscribers_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id',
                  'username',
                  'email',
                  'first_name',
                  'last_name',
                  'subscribers_count',
                  'is_subscribed')

    def get_is_subscribed(self, master):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.subscriptions.filter(master=master).exists()

    def get_subscribers_count(self, master):
        return master.subscribers.all().count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для Тегов."""
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id',
                  'name',
                  'slug',
                  'color')


class ActivitySerializer(serializers.ModelSerializer):
    """Сериализатор для Активностей."""

    class Meta:
        model = Activity
        fields = ('id',
                  'name',
                  'description',
                  'slug')


class ServiceSerializer(serializers.ModelSerializer):
    """Сериализатор для создания-обновления Сервисов."""
    master = CustomUserContextSerializer(
        default=serializers.CurrentUserDefault()
    )
    activities = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    locations = serializers.SerializerMethodField()
    image = Base64ImageField()
    created = serializers.DateTimeField(format='%Y-%m-%d')
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ('id',
                  'name',
                  'description',
                  'master',
                  'activities',
                  'tags',
                  'locations',
                  'image',
                  'created',
                  'is_favorited')

        validators = [
            UniqueTogetherValidator(queryset=Service.objects.all(),
                                    fields=['master', 'name'])
        ]

    def validate(self, data):
        tags_list = self.initial_data.get('tags')
        activities_list = self.initial_data.get('activities')
        locations_list = self.initial_data.get('locations')

        tags = get_validated_field(tags_list, Tag)
        activities = get_validated_field(activities_list, Activity)
        locations = get_validated_field(locations_list, Location)

        data.update({'tags': tags,
                     'activities': activities,
                     'locations': locations})

        return data

    def create(self, validated_data):
        tags_list = validated_data.pop('tags')
        activity_list = validated_data.pop('activities')
        location_list = validated_data.pop('locations')
        service = Service.objects.create(**validated_data)

        service.tags.set(tags_list)
        service.activities.set(activity_list)
        service.locations.set(location_list)

        return service

    def update(self, instance, validated_data):
        tags_list = validated_data.pop('tags')
        activity_list = validated_data.pop('activities')
        location_list = validated_data.pop('locations')
        instance = super().update(instance, validated_data)
        instance.save()

        instance.tags.clear()
        instance.tags.set(tags_list)

        instance.activities.clear()
        instance.activities.set(activity_list)

        instance.locations.clear()
        instance.activities.set(location_list)

        return instance

    def get_tags(self, service):
        return service.tags.values()

    def get_activities(self, service):
        return service.activities.values()

    def get_locations(self, service):
        return service.locations.values()

    def get_is_favorited(self, service):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.favorite_services.filter(service=service).exists()


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов к Сервисам."""
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'score', 'author', 'pub_date')

    def validate(self, data):
        request = self.context['request']
        author = request.user
        service = get_object_or_404(
            Service, pk=self.context['view'].kwargs.get('id')
        )
        if request.method == 'POST':
            if Review.objects.filter(service=service, author=author):
                raise ValidationError('Можно оставить только один отзыв')
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к отзывам."""
    review = ReviewSerializer(read_only=True)
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'review', 'text', 'author', 'pub_date')
