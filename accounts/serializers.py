from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes,smart_str,DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator 
from rest_framework import serializers
from accounts.models import CustomUser
from .utils import Utils


class UserRegistrationSerializer(serializers.ModelSerializer):
    password2=serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model=CustomUser
        fields=['email','first_name','last_name','password','password2']
        extra_kwargs={
            'password':{'write_only':True}
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password Doesn't match")
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('password2', None)
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserLoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=255)
    class Meta:
        model=CustomUser
        fields=['email','password']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomUser
        fields=['email','first_name','last_name']

class UserChangePasswordSerializer(serializers.ModelSerializer):
    password=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
    password2=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
    class Meta:
        model=CustomUser
        fields=['password','password2']

    def validate(self,attrs):
        password=attrs.get('password')
        password2=attrs.get('password2')
        user=self.context.get('user')
        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password Doesn't match")
        user.set_password(password)
        user.save()
        return attrs
class UserResetPasswordEmailSerializer(serializers.Serializer):
    email=serializers.EmailField(max_length=255)
    def validate(self, attrs):
        email=attrs.get('email')
        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email=email)
            uid=urlsafe_base64_encode(force_bytes(user.pk))
            token=PasswordResetTokenGenerator().make_token(user)
            link="http://127.0.0.1:8000/accounts/reset-password/"+uid+"/"+token
            print('link',link)
            #send email
            body='Click on link to reset your password'+link
            data={
                'subject':'Reset Your Password',
                'body':body,
                'to_email':user.email
            }
            Utils.send_email(data)
            
        else:
            raise serializers.ValidationError('You are not Registered User')
        return attrs
class UserResetPasswordSerializer(serializers.Serializer):
    password=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
    password2=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
    class Meta:
        model=CustomUser
        fields=['password','password2']

    def validate(self,attrs):
        password=attrs.get('password')
        password2=attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password Doesn't match")
        uidb64=self.context.get('uid')
        token=self.context.get('token')
        try:
            uid = smart_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (CustomUser.DoesNotExist, DjangoUnicodeDecodeError):
            raise serializers.ValidationError('Invalid reset link')
        if not PasswordResetTokenGenerator().check_token(user,token):
            raise serializers.ValidationError('Token is not Valid')
        user.set_password(password)
        user.save()
        return attrs

