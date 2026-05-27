from rest_framework import serializers
from .models import Report


class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['target_type', 'target_id', 'target_preview', 'reason', 'description']

    def create(self, validated_data):
        validated_data['reporter'] = self.context['request'].user
        return super().create(validated_data)


class ReportAdminSerializer(serializers.ModelSerializer):
    reporter_name = serializers.SerializerMethodField()
    reviewer_name = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'id', 'reporter', 'reporter_name',
            'target_type', 'target_id', 'target_preview',
            'reason', 'description',
            'status', 'admin_note',
            'reviewed_by', 'reviewer_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'reporter', 'reporter_name',
            'target_type', 'target_id', 'target_preview',
            'reason', 'description',
            'reviewed_by', 'reviewer_name',
            'created_at', 'updated_at',
        ]

    def get_reporter_name(self, obj):
        if obj.reporter:
            return obj.reporter.full_name or obj.reporter.username
        return 'Deleted User'

    def get_reviewer_name(self, obj):
        if obj.reviewed_by:
            return obj.reviewed_by.full_name or obj.reviewed_by.username
        return None

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            instance.reviewed_by = request.user
        instance.status = validated_data.get('status', instance.status)
        instance.admin_note = validated_data.get('admin_note', instance.admin_note)
        instance.save()
        return instance