import re
import webcolors

from django.contrib.auth import authenticate
from django.db import transaction
from django.shortcuts import get_object_or_404

from drf_extra_fields.fields import Base64ImageField

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from djoser.serializers import (UserSerializer,
                                UserCreateSerializer,
                                TokenCreateSerializer)

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
    """Сериализатор отображения профиля рецепта в других контекстах."""
    activities = serializers.StringRelatedField(many=True)

    class Meta:
        model = Service
        fields = ('id',
                  'name',
                  'activities')


class RegisterUserSerializer(UserCreateSerializer):
    """Кастомный базовый сериализатор регистрации пользователя."""

    class Meta:
        model = CustomUser
        fields = ('id',
                  'username',
                  'email',
                  'first_name',
                  'last_name',
                  'phone_number',
                  'password',
                  'photo',)

    def validate_username(self, data):
        username = data
        error_symbols_list = []

        for symbol in username:
            if not re.search(r'^[\w.@+-]+\Z', symbol):
                error_symbols_list.append(symbol)
        if error_symbols_list:
            raise serializers.ValidationError(
                f'Символы {"".join(error_symbols_list)} недопустимы'
            )
        return data


class RegisterMasterSerializer(RegisterUserSerializer):
    """Кастомный сериализатор регистрации Мастера."""

    class Meta:
        model = CustomUser
        fields = RegisterUserSerializer.Meta.fields + ('is_master',)


class RegisterClientSerializer(RegisterUserSerializer):
    """Кастомный сериализатор регистрации Клиента."""
    pass


class CustomTokenCreateSerializer(TokenCreateSerializer):
    """Кастомный сериализатор получения токена по email/номеру телефона"""

    password = serializers.CharField(
        required=False, style={'input_type': 'password'}
    )
    field = CustomUser.USERNAME_FIELD
    alt_field = CustomUser.ALT_USERNAME_FIELD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

        if self.context['request'].data.get(self.field):
            self.fields[self.field] = serializers.CharField(required=False)
        else:
            self.fields[self.alt_field] = serializers.CharField(required=False)

    def validate(self, data):
        password = data.get('password')

        params = {}
        if self.context['request'].data.get(self.field):
            params = {self.field: data.get(self.field)}
        else:
            params = {self.alt_field: data.get(self.alt_field)}
        self.user = authenticate(
            request=self.context.get('request'), **params, password=password
        )

        if not self.user:
            self.user = CustomUser.objects.filter(**params).first()
            if self.user and not self.user.check_password(password):
                raise serializers.ValidationError(
                    'Некорректный пароль пользователя!'
                )
        if self.user and self.user.is_active:
            return data
        raise serializers.ValidationError(
            'Некорректные данные пользователя!'
        )


class CustomUserSerializer(UserSerializer):
    """Кастомный базовый сериализатор всех пользователей."""
    pass


class MasterSerializer(CustomUserSerializer):
    """Кастомный сериализатор Мастера."""
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
    """Кастомный сериализатор Клиента."""
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
    """Кастомный сериализатор профиля Мастера в других контекстах."""
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
    """Сериализатор Тегов."""
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id',
                  'name',
                  'slug',
                  'color')


class ActivitySerializer(serializers.ModelSerializer):
    """Сериализатор Активностей."""

    class Meta:
        model = Activity
        fields = ('id',
                  'name',
                  'description',
                  'slug')


class LocationSerializer(serializers.ModelSerializer):
    """Сериализатор Локации."""

    class Meta:
        model = Location
        fields = ('id',
                  'country',
                  'city',
                  'street',
                  'house_number',
                  'building',
                  'office_number')


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор Комментариев к Отзывам."""
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True
    )
    pub_date = serializers.DateTimeField(read_only=True, format='%d.%m.%Y')

    class Meta:
        model = Comment
        fields = ('id',
                  'review',
                  'text',
                  'author',
                  'pub_date')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор Отзывов к Сервисам."""
    service = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True
    )
    pub_date = serializers.DateTimeField(read_only=True, format='%d.%m.%Y')
    comments = CommentSerializer(read_only=True, many=True)

    class Meta:
        model = Review
        fields = ('id',
                  'service',
                  'author',
                  'text',
                  'score',
                  'pub_date',
                  'comments')

    def validate(self, data):
        request = self.context['request']
        author = request.user
        service = get_object_or_404(
            Service, pk=self.context['view'].kwargs.get('service_id')
        )
        if author == service.master:
            raise ValidationError(
                'Запрещено оставлять отзыв о качестве собственных услуг'
            )
        if request.method == 'POST':
            if Review.objects.filter(service=service, author=author):
                raise ValidationError('Можно оставить только один отзыв')
        return data


class ReviewContextSerializer(serializers.ModelSerializer):
    """Сериализатор Отзывов к Сервисам в других контекстах."""
    pub_date = serializers.DateTimeField(read_only=True, format='%d.%m.%Y')

    class Meta:
        model = Review
        fields = ('id', 'text', 'score', 'author', 'pub_date')


class ServiceSerializer(serializers.ModelSerializer):
    """Сериализатор Сервиса."""
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
    created = serializers.DateTimeField(read_only=True, format='%d.%m.%Y')
    reviews = ReviewContextSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(read_only=True)
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
                  'reviews',
                  'rating',
                  'is_favorited')

        validators = [
            UniqueTogetherValidator(queryset=Service.objects.all(),
                                    fields=['master', 'name'])
        ]

    # def validate(self, data):
    #     activities_list = self.initial_data('activities')
    #     tags_list = self.initial_data('tags')

    #     activities = get_validated_field(activities_list, Activity)
    #     tags = get_validated_field(tags_list, Tag)

    #     data.update({'activities': activities,
    #                  'tags': tags})
    #     return data
    @transaction.atomic
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
