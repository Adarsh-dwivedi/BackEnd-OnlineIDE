from rest_framework import serializers
from .models import Submission
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["username", "password", "email"]
        model = User
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Submission