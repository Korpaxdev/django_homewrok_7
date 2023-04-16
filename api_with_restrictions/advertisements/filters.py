from django_filters import rest_framework as filters

from advertisements.models import Advertisement, UserFavoriteAdvertisements


class AdvertisementFilter(filters.FilterSet):
    """Фильтры для объявлений."""
    creator = filters.CharFilter(field_name='creator__username')
    created_at = filters.DateFromToRangeFilter(field_name='created_at')


    class Meta:
        model = Advertisement
        fields = ('creator', 'created_at',)


class FavoriteAdvertisementsFilter(filters.FilterSet):
    favorite_id = filters.NumberFilter(field_name='id')
    id = filters.NumberFilter(field_name='advertisement__id')
    creator = filters.CharFilter(field_name='advertisement__creator__username')
    added_at = filters.DateFromToRangeFilter(field_name='added_at')

    class Meta:
        model = UserFavoriteAdvertisements
        fields = ('favorite_id', 'id', 'creator', 'added_at')
