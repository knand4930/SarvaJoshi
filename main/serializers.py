import imp
from rest_framework import serializers
from .models import Profile, User, Role
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


# class UserUpdateSerializer()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "fname", "lname", "phone", "email", "address", "city", "state", "country", "image", "image"]
        extra_kwargs = {
            "id": {"read_only": True},
            # "fname": {"required": True},
            # "lname": {"required": True},
            "phone": {"required": True},
            # "email": {"required": True},
        }

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'mobile', 'image', 'name', 'address', 'location')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", 'phone', "fname", "lname", "email", "address", "verified")


class UpdateUserSerializer(serializers.ModelSerializer):
    # email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ("id", 'phone', 'fname', 'lname', 'email', 'address')
        # extra_kwargs = {
        #     'first_name': {'required': True},
        #     'last_name': {'required': True},
        # }

    # def validate_email(self, value):
    #     user = self.context['request'].user
    #     if User.objects.exclude(pk=user.pk).filter(email=value).exists():
    #         raise serializers.ValidationError({"email": "This email is already in use."})
    #     return value
    #
    # def validate_username(self, value):
    #     user = self.context['request'].user
    #     if User.objects.exclude(pk=user.pk).filter(username=value).exists():
    #         raise serializers.ValidationError({"username": "This username is already in use."})
    #     return value

    def update(self, instance, validated_data):
        instance.fname = validated_data['fname']
        instance.lname = validated_data['lname']
        instance.email = validated_data['email']
        instance.phone = validated_data['phone']
        instance.address = validated_data['address']

        instance.save()

        return instance