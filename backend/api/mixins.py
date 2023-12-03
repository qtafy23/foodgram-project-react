from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type
from rest_framework import mixins, viewsets


if TYPE_CHECKING:
    from rest_framework.serializers import Serializer


class MultiSerializerViewSetMixin:
    """Миксин для выбора подходящего сериалайзера из `serializer_classes`."""

    serializer_classes: Optional[dict[str, Type[Serializer]]] = None

    def get_serializer_class(self):
        try:
            return self.serializer_classes[self.action]
        except KeyError:
            return super().get_serializer_class()


class CreateListRetrieveViewSetMixin(
    MultiSerializerViewSetMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    pass


class ModelMultiSerializerViewSetMixin(
    MultiSerializerViewSetMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    pass
