from rest_framework import serializers
from .models import Candidate, CandidateStatus


class CandidateSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = '__all__'

    def get_status(self, obj):
        status = obj.status.first()
        return CandidateStatusSerializer(status).data['status'] if status else None

    def create(self, validated_data):
        candidate = super().create(validated_data)
        CandidateStatus.objects.create(candidateId=candidate, status='registered')
        return candidate


class CandidateStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = CandidateStatus
        fields = '__all__'




