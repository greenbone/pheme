from dataclasses import dataclass
from rest_framework import generics, serializers


@dataclass
class Test:
    name: str


class TestSerializer(serializers.Serializer):
    name = serializers.CharField()

    def update(self, instance, validated_data):
        raise NotImplementedError('`update()` must be implemented.')

    def create(self, validated_data):
        raise NotImplementedError('`create()` must be implemented.')


class TestView(generics.ListAPIView):  # new
    queryset = iter([Test("1"), Test("2")])
    serializer_class = TestSerializer
