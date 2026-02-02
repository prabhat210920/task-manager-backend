from rest_framework import serializers
from .models import Goal, DailyLog

class DailyLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyLog
        fields = ['id', 'date', 'amount', 'note', 'created_at']
        read_only_fields = ['id', 'created_at']

class GoalSerializer(serializers.ModelSerializer):
    logs = DailyLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = Goal
        fields = [
            'id', 'title', 'total_units', 'units_completed', 
            'unit_name', 'start_date', 'end_date', 
            'progress_percentage', 'logs', 'created_at'
        ]
        read_only_fields = ['id', 'units_completed', 'created_at', 'progress_percentage']

    def create(self, validated_data):
        user = self.context['request'].user
        return Goal.objects.create(user=user, **validated_data)
