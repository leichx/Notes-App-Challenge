from rest_framework import serializers
from api.notes.models import Note
from api.users.models import Category
from api.users.serializers import CategorySerializer

class NoteSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = Note
        fields = (
            'id', 'title', 'content', 'category', 'category_id',
            'created_at', 'updated_at', 'user_id'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'user_id')

    def validate_category_id(self, value):
        try:
            category = Category.objects.get(id=value)
            return value
        except Category.DoesNotExist:
            raise serializers.ValidationError("Invalid category ID")

    def create(self, validated_data):
        category_id = validated_data.pop('category_id')
        category = Category.objects.get(id=category_id)
        return Note.objects.create(
            category=category,
            **validated_data
        )

    def update(self, instance, validated_data):
        # Validate category_id if provided
        if 'category_id' in validated_data:
            category_id = validated_data.pop('category_id')
            try:
                category = Category.objects.get(id=category_id)
                instance.category = category
            except Category.DoesNotExist:
                raise serializers.ValidationError({
                    "category_id": "Invalid category ID"
                })
        
        # Update other fields
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance
