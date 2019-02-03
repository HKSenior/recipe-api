from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """
        Serializer for the users object.
    """

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8
            }
        }

    def create(self, validated_data):
        """
            Create a new user with an encrypted password
            and return the user.
        """
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """
            Update a user, setting the password correctly
            and return it.
        """
        # Retrieve and remove the password from validated_data
        password = validated_data.pop('password', None)

        # Update the data
        user = super().update(instance, validated_data)

        # Set the password
        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """
        Serializer for the user authentication object.
    """
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """
            Validate and authenticate the user.
        """
        # Get the email and password fields
        email = attrs.get('email')
        password = attrs.get('password')

        # Authenticate the user
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        # Check if the user wasn't created
        if not user:
            msg = _('Unable to authenticate with the provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        # Set the user in the attributes and return it
        attrs['user'] = user
        return attrs
