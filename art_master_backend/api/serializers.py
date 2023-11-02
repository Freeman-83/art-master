# from rest_framework.fields import empty
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
                             LocationService,
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


class RegisterSerializer(UserCreateSerializer):
    """Кастомный базовый сериализатор для регистрации пользователя."""
    pass


class RegisterMasterSerializer(RegisterSerializer):
    """Кастомный сериализатор для регистрации Мастера."""
    # photo = Base64ImageField()

    class Meta:
        model = CustomUser
        fields = ('id',
                  'username',
                  'email',
                  'first_name',
                  'last_name',
                  'password',
                  'photo',
                  'is_master')


class RegisterClientSerializer(RegisterSerializer):
    """Кастомный сериализатор для регистрации Клиента."""

    class Meta:
        model = CustomUser
        fields = ('id',
                  'username',
                  'email',
                  'first_name',
                  'last_name',
                  'password',
                  'photo')


class CustomUserSerializer(UserSerializer):
    """Кастомный базовый сериализатор для всех пользователей."""
    pass


class MasterSerializer(CustomUserSerializer):
    """Кастомный сериализатор для Мастера."""
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
                  'services',
                  'subscribers_count',
                  'is_subscribed')

    def get_is_subscribed(self, master):
        client = self.context['request'].user
        if client.is_anonymous:
            return False
        return client.subscriptions.filter(master=master).exists()

    def get_subscribers_count(self, master):
        return master.subscribers.all().count()


class ClientSerializer(CustomUserSerializer):
    """Кастомный сериализатор для Клиента."""
    subscriptions_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id',
                  'username',
                  'email',
                  'first_name',
                  'last_name',
                  'subscriptions_count')

    def get_subscriptions_count(self, client):
        return client.subscriptions.all().count()


class MasterContextSerializer(CustomUserSerializer):
    """ Кастомный сериализатор для отображения профиля Мастера
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


class LocationSerializer(serializers.ModelSerializer):
    """Сериализатор для Локации."""

    class Meta:
        model = Location
        fields = ('country',
                  'city',
                  'street',
                  'house_number',
                  'building',
                  'office_number')


class ServiceSerializer(serializers.ModelSerializer):
    """Сериализатор для Сервиса."""
    master = MasterContextSerializer(
        default=serializers.CurrentUserDefault()
    )
    activities = serializers.PrimaryKeyRelatedField(
        queryset=Activity.objects.all(), many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    locations = LocationSerializer(many=True)
    image = Base64ImageField()
    site_address = serializers.URLField(required=False)
    created = serializers.DateTimeField(read_only=True, format='%Y-%m-%d')
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ('id',
                  'name',
                  'description',
                  'activities',
                  'tags',
                  'master',
                  'locations',
                  'site_address',
                  'phone_number',
                  'social_network_contacts',
                  'image',
                  'created',
                  'is_favorited')

        validators = [
            UniqueTogetherValidator(queryset=Service.objects.all(),
                                    fields=['master', 'name'])
        ]

    def create(self, validated_data):
        locations_list = validated_data.pop('locations')
        activities_list = validated_data.pop('activities')
        tags_list = validated_data.pop('tags')

        service = Service.objects.create(**validated_data)

        service.activities.set(activities_list)
        service.tags.set(tags_list)

        for location in locations_list:
            current_location = Location.objects.create(**location)
            LocationService.objects.create(
                location=current_location, service=service
            )

        return service

    def get_is_favorited(self, service):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.favorite_services.filter(service=service).exists()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['activities'] = instance.activities.values()
        data['tags'] = instance.tags.values()
        return data


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
