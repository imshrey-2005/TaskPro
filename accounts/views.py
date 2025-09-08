from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import status
from .serializers import UserRegistrationSerializer,UserLoginSerializer,UserProfileSerializer,UserChangePasswordSerializer,UserResetPasswordEmailSerializer,UserResetPasswordSerializer
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


def get_tokens_for_user(user):
    if not user.is_active:
      raise AuthenticationFailed("User is not active")

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def home_view(request):
    if request.user.is_authenticated:
        #need to show task dashboard
        return redirect('tasklist')
    return render(request, 'index.html')
class UserRegistrationView(GenericAPIView):
    permission_classes=[AllowAny,]
    serializer_class = UserRegistrationSerializer

    def get(self, request):
        return render(request, 'accounts/register.html')

    def post(self,request):
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid():
            user=serializer.save()
            token=get_tokens_for_user(user)
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
        else:
            for field, errors in serializer.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return render(request, 'accounts/register.html')

class UserLoginView(GenericAPIView):
    permission_classes=[AllowAny,]
    serializer_class = UserLoginSerializer

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('profile')
        return render(request, 'accounts/login.html')

    def post(self, request):
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid():
            email=serializer.data.get('email')
            password=serializer.data.get('password')
            user=authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                token=get_tokens_for_user(user)
                messages.success(request, f'Welcome back, {user.first_name or user.email}!')
                return redirect('profile')
            else:
                messages.error(request, 'Email or Password is not valid')
                return render(request, 'accounts/login.html')
        else:
            for field, errors in serializer.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return render(request, 'accounts/login.html')

class UserLogoutAPIView(GenericAPIView):
    """
    An endpoint to logout users.
    """

    permission_classes = [IsAuthenticated,]

    def get(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return render(request,'accounts/logout.html')
        

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            logout(request)
            messages.success(request, 'You have been successfully logged out.')
            return render(request,'accounts/logout.html')
        except Exception as e:
            logout(request)
            messages.success(request, 'You have been successfully logged out.')
            return render(request,'accounts/logout.html')

class UserProfileView(GenericAPIView):
    permission_classes=[IsAuthenticated,]
    serializer_class=UserProfileSerializer

    def get(self,request):
        return render(request, 'accounts/profile.html', {'user': request.user})

    def handle_exception(self, exc):
        from rest_framework.exceptions import NotAuthenticated
        if isinstance(exc, NotAuthenticated):
            if self.request.accepts('text/html'):
                messages.error(self.request, 'Please log in to view your profile.')
                return redirect('login')
        return super().handle_exception(exc)

class UserChangePasswordView(GenericAPIView):
    serializer_class=UserChangePasswordSerializer
    

    def get(self, request):
        return render(request, 'accounts/change_password.html')

    def post(self,request):
        serializer=self.get_serializer(data=request.data,context={'user':request.user})
        if serializer.is_valid():
            messages.success(request, 'Password changed successfully!')
            return redirect('profile')
        else:
            for field, errors in serializer.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return render(request, 'accounts/change_password.html')

class UserResetPasswordEmailView(GenericAPIView):
    serializer_class=UserResetPasswordEmailSerializer
    
    def get(self, request):
        return render(request, 'accounts/reset_password_email.html')
    
    def post(self,request):
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid():
            messages.success(request, 'Password reset email sent to your address. Please check your inbox.')
            return redirect('login')
        else:
            for field, errors in serializer.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return render(request, 'accounts/reset_password_email.html')


class UserResetPasswordView(GenericAPIView):
   
    serializer_class=UserResetPasswordSerializer
    
    def get(self, request, uid, token):
        return render(request, 'accounts/reset_password.html', {'uid': uid, 'token': token})
    
    def post(self,request,uid,token):
        serializer=self.get_serializer(data=request.data,context={'uid':uid,'token':token})
        if serializer.is_valid():
            messages.success(request, 'Password reset successfully! You can now log in with your new password.')
            return redirect('login')
        else:
            for field, errors in serializer.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return render(request, 'accounts/reset_password.html', {'uid': uid, 'token': token})



    

