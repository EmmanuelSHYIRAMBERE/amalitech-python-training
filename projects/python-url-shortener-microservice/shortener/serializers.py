from rest_framework import serializers
from .models import URL


class URLCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = URL
        fields = ["original_url"]

    def create(self, validated_data):
        from .models import generate_short_code
        return URL.objects.create(
            short_code=generate_short_code(),
            **validated_data,
        )


class URLResponseSerializer(serializers.ModelSerializer):
    short_url = serializers.SerializerMethodField()

    class Meta:
        model = URL
        fields = ["short_code", "original_url", "short_url", "created_at"]

    def get_short_url(self, obj) -> str:
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(f"/{obj.short_code}/")
        return f"/{obj.short_code}/"
