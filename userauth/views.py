from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from .serializers import UserRegisterSerializer, LoginSerializer, PasswordResetRequestSerializer, SetNewPasswordSerializer, LogoutUserSerializer
from rest_framework.response import Response
from rest_framework import status
from .utils import send_otp_email
from .models import EmailOTP, User
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator

# Create your views here.
class RegisterUserView(GenericAPIView):
    """
    API endpoint for registering a new user.
    """
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]  # Allow anyone to register

    def post(self, request):
        """
        Register a new user and send OTP email.
        """
        user_data = request.data
        serializer = self.serializer_class(data=user_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user = serializer.data

            #SEND EMAIL FUNCTION
            #send_otp_email(user['email'])
            return Response({
                'data':user,
                'message':f"hi your OTP has been sent to your Email"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class VerifyUserEmail(GenericAPIView):
    """
    API endpoint for verifying a user's email using OTP.
    """
    def post(self, request):
        otpcode = request.data.get('otp')
        try:
            user_code_obj = EmailOTP.objects.get(otp=otpcode)
            user = user_code_obj.user
            if not user.is_verified:
                user.is_verified=True
                user.save()
                return Response({
                    'message':'Account email verified successfully'
                }, status=status.HTTP_200_OK)
            return Response({
                'message':'Code is invalid user already verified'
            }, status=status.HTTP_204_NO_CONTENT)
        
        except EmailOTP.DoesNotExist:
            return Response({'message':'OTP not provided'}, status=status.HTTP_404_NOT_FOUND)
        



class LoginUserView(GenericAPIView):
    """
    API endpoint for user login.
    """
    serializer_class=LoginSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    

class PasswordResetRequestView(GenericAPIView):
    """
    API endpoint to request a password reset email.
    """
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        return Response({'message':'we have sent you a link to reset your password'}, status=status.HTTP_200_OK)
    


class PasswordResetConfirm(GenericAPIView):
    """
    API endpoint to confirm password reset token and UID.
    """

    def get(self, request, uidb64, token):
        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'message':'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success':True, 'message':'credentials is valid', 'uidb64':uidb64, 'token':token}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError as identifier:
            return Response({'message':'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        


class SetNewPasswordView(GenericAPIView):
    """
    API endpoint to set a new password after reset.
    """
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success':True, 'message':"password reset is succesful"}, status=status.HTTP_200_OK)
    


class LogoutApiView(GenericAPIView):
    """
    API endpoint to log out a user and blacklist their refresh token.
    """
    serializer_class = LogoutUserSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)