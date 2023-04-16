from django.contrib.auth.models import User
from rest_framework import serializers

from advertisements.models import Advertisement, AdvertisementStatusChoices, UserFavoriteAdvertisements


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""
    MAX_OPENED_ADV = 10
    creator = UserSerializer(
        read_only=True
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at',)

    def create(self, validated_data):
        """Метод для создания"""

        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""

        status = data.get('status', AdvertisementStatusChoices.OPEN)

        if status == AdvertisementStatusChoices.OPEN:
            open_count = Advertisement.objects.filter(creator=self.context["request"].user,
                                                      status=status).count()
            if open_count >= self.MAX_OPENED_ADV:
                raise serializers.ValidationError({'detail': 'Превышен лимит по открытым объявлениям'})

        return data


class UserFavoriteAdvertisementsSerializer(serializers.ModelSerializer):
    favorite_id = serializers.IntegerField(source='id')
    advertisement = AdvertisementSerializer()

    class Meta:
        model = UserFavoriteAdvertisements
        fields = ('favorite_id', 'advertisement', 'added_at')
