from urllib.parse import urlparse

from django.core.validators import URLValidator

from rest_framework import serializers


class DomainField(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        if not data.startswith("http"):
            data = f"http://{data}"
        URLValidator()(data)
        parsed = urlparse(data)
        if not parsed.netloc:
            raise serializers.ValidationError("Incorrect URL")
        return parsed.netloc


class DomainSaveSerializer(serializers.Serializer):
    links = serializers.ListField(child=DomainField(required=True), min_length=1)


class DomainFilterSerializer(serializers.Serializer):
    def get_fields(self):
        # "from" is reserved python word
        # so in order to create serializer field properly
        # I use this method
        return {
            "from": serializers.FloatField(required=True),
            "to": serializers.FloatField(required=True),
        }
