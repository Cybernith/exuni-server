from typing import List

from rest_framework.generics import get_object_or_404

from helpers.models import manage_files


class MassRelatedCUD:

    def __init__(
            self,
            user,
            items: List,
            ids_to_delete: List,
            parent_field,
            parent_id,
            create_serializer,
            update_serializer,
    ):
        self.user = user
        self.items = items or []
        self.ids_to_delete = ids_to_delete or []
        self.parent_id = parent_id
        self.parent_field = parent_field
        self.create_serializer = create_serializer
        self.update_serializer = update_serializer

    def sync(self):

        model = self.create_serializer.Meta.model

        items_to_create = []
        items_to_update = []

        for item in self.items:
            item[self.parent_field] = self.parent_id
            if hasattr(self.create_serializer.Meta.model, 'order'):
                item['order'] = self.items.index(item)
            if 'id' in item and item['id']:
                items_to_update.append(item)
            else:
                items_to_create.append(item)

        serializer = self.create_serializer(data=items_to_create, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        for item in items_to_update:
            instance = get_object_or_404(model.objects.all(), id=item['id'])

            manage_files(instance, item, ['attachment'])

            serializer = self.update_serializer(instance, data=item)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

        for item_id in self.ids_to_delete:
            instance = get_object_or_404(model.objects.all(), id=item_id)
            self.perform_delete(instance)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def perform_delete(self, instance):
        instance.delete()
