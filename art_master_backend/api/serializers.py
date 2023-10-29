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
    role = serializers.ChoiceField(choices=CustomUser.ROLE, default='master')
    bio = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)

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
                  'photo',
                  'phone_number')


class RegisterClientSerializer(RegisterSerializer):
    """Кастомный сериализатор для регистрации Клиента."""

    class Meta:
        model = CustomUser
        fields = ('id',
                  'username',
                  'email',
                  'first_name',
                  'last_name',
                  'password',)


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
                  'role',
                  'services',
                  'subscribers_count',
                  'is_subscribed')

    # def validate(self, data):
    #     if self.initial_data.get('role') == 'master':
    #         bio = self.initial_data.get('bio')
    #         photo = self.initial_data.get('photo')
    #         phone_number = self.initial_data.get('phone_number')

    #         if not all([bio, photo, phone_number]):
    #             raise ValidationError(
    #                 'Для пользователя со статусом МАСТЕР '
    #                 'поля О СЕБЕ, ФОТО и НОМЕР ТЕЛЕФОНА обязательны!'
    #             )
    #         data.update({'bio': bio,
    #                      'photo': photo,
    #                      'phone_number': phone_number})

    #     return data

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
                  'role',
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


class ServiceSerializer(serializers.ModelSerializer):
    """Сериализатор для создания-обновления Сервисов."""
    master = MasterContextSerializer(
        default=serializers.CurrentUserDefault()
    )
    activities = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    locations = serializers.SerializerMethodField()
    image = Base64ImageField()
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

    def update(self, instance, validated_data):

        for item in validated_data:
            elem = validated_data.pop(item, instance.item)
            instance.item.clear()
            instance.item.set(elem)

        instance.save()

        # tags_list = validated_data.pop('tags', instance)
        # activity_list = validated_data.pop('activities', instance)
        # location_list = validated_data.pop('locations', instance)
        # instance = super().update(instance, validated_data)
        # instance.save()

        # instance.tags.clear()
        # instance.tags.set(tags_list)

        # instance.activities.clear()
        # instance.activities.set(activity_list)

        # instance.locations.clear()
        # instance.activities.set(location_list)

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
