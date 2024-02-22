from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    def create(self, validated_data):
        """override; create and return user with encrypt password"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):  # instance is the user that is going to get updated
        """override; update and return user"""
        password = validated_data.pop('password', None)  # get the password from the validated_data dict then remove it
        # the none value means that if the password is not in the dict just return null value, so it doesn't force it
        user = super().update(instance, validated_data)  # super().update calls def update of the bass class.

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """serializer for the user auth token"""
    email = serializers.EmailField()  # serializes two field email and password with no model needed
    password = serializers.CharField(
        style={'input_type': 'password'},  # text hidden while input
        trim_whitespace=False,
    )

    def validate(self, attrs):  # attrs is the all the attributes that is provided by the serializer
        """validate and auth the user during validations of that serializer"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(  # this will check if username and password is correct if not it will return empty object
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:  # if the object is empty
            msg = _('unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user  # if successful the attrs will set to the user and return it for the view
        return attrs
