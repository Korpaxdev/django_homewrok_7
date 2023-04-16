from django import shortcuts
from django.db import IntegrityError, models
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import viewsets, permissions, decorators, mixins
from rest_framework.response import Response

from advertisements.filters import AdvertisementFilter, FavoriteAdvertisementsFilter
from advertisements.models import Advertisement, AdvertisementStatusChoices, UserFavoriteAdvertisements
from advertisements.permisions import IsOwnerOrReadOnly, IsSuperUser
from advertisements.serializers import AdvertisementSerializer, UserFavoriteAdvertisementsSerializer


class AdvertisementViewSet(viewsets.ModelViewSet):
    """ViewSet для объявлений."""
    queryset = Advertisement.objects.all().order_by('id')
    serializer_class = AdvertisementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdvertisementFilter
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly | IsSuperUser, ]

    def get_queryset(self):
        """
        Модифицирует queryset в зависимости от пользователя.
        Не авторизованный - возвращает все объявления и исключает из них DRAFT
        Суперпользователь - возвращает стандартный queryset со всеми объявлениями
        Авторизованный - возвращает все объявления без статуса DRAFT, а если есть DRAFT то возвращает их в случае если
        пользователь владелец объявления
        """
        user = self.request.user
        if not user.is_authenticated:
            return self.queryset.exclude(status=AdvertisementStatusChoices.DRAFT)
        if user.is_superuser:
            return self.queryset
        return self.queryset.exclude(
            models.Q(status=AdvertisementStatusChoices.DRAFT) & ~models.Q(creator=self.request.user))

    @decorators.action(methods=['POST'], detail=True, permission_classes=[permissions.IsAuthenticated])
    def add_to_favorite(self, request, pk):
        """
        Добавляет объявление в избранное пользователя с проверками (на то что пользователь не владелец объявления,
        на уникальность объявления в избранном
        """
        advertisement = shortcuts.get_object_or_404(self.queryset, pk=pk)
        if advertisement.creator == self.request.user:
            return Response({'error': 'Вы не можете добавлять свое объявление в избранное'},
                            status=status.HTTP_409_CONFLICT)
        try:
            UserFavoriteAdvertisements.objects.create(user=request.user, advertisement=advertisement)
            return Response({'detail': 'Успешно добавлено'})
        except IntegrityError:
            return Response({'error': 'Объявление уже есть в списке избранного'}, status=status.HTTP_409_CONFLICT)


class UserFavoriteViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    """
    ViewSet для списка избранных объявлений.
    """
    serializer_class = UserFavoriteAdvertisementsSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = FavoriteAdvertisementsFilter

    def get_queryset(self):
        return UserFavoriteAdvertisements.objects.filter(user=self.request.user)
