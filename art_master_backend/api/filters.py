from django_filters.rest_framework import (FilterSet,
                                           BooleanFilter,
                                           CharFilter,
                                           ModelMultipleChoiceFilter)

from services.models import (Activity,
                             Service,
                             Tag)


class ActivityFilterSet(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Activity
        fields = ('name',)


class ServiceFilterSet(FilterSet):
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    activity = ModelMultipleChoiceFilter(
        field_name='activity__slug',
        to_field_name='slug',
        queryset=Activity.objects.all()
    )
    is_favorited = BooleanFilter(
        field_name='in_favorite_for_users',
        method='is_exist_filter'
    )

    class Meta:
        model = Service
        fields = ('tags', 'author')

    def is_exist_filter(self, queryset, name, value):
        lookup = '__'.join([name, 'user'])
        if self.request.user.is_anonymous:
            return queryset
        return queryset.filter(**{lookup: self.request.user})
