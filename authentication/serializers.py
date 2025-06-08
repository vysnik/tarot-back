from rest_framework import serializers
from .models import CustomUser


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CustomUser
        fields = (
            "email",
            "first_name",
            "last_name",
            "birth_date",
            "gender",
            "bio",
            "profile_completed",
        )
        read_only_fields = ("email",)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        required = ["first_name", "last_name", "birth_date", "gender", "bio"]
        instance.profile_completed = all(getattr(instance, f) for f in required)

        instance.save()
        return instance