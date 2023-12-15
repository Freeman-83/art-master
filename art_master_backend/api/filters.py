from django_filters.rest_framework import (FilterSet,
                                           BooleanFilter,
                                           CharFilter,
                                           ModelMultipleChoiceFilter)

from services.models import (Activity,
                             Service)


class ActivityFilterSet(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Activity
        fields = ('name',)


class ServiceFilterSet(FilterSet):

    activities = ModelMultipleChoiceFilter(
        field_name='activity__slug',
        to_field_name='slug',
        queryset=Activity.objects.all()
    )
    is_favorited = BooleanFilter(
        field_name='in_favorite_for_clients',
        method='is_exist_filter'
    )

    class Meta:
        model = Service
        fields = ('activities',)

    def is_exist_filter(self, queryset, name, value):
        lookup = '__'.join([name, 'client'])
        if self.request.user.is_anonymous:
            return queryset
        return queryset.filter(**{lookup: self.request.user})
