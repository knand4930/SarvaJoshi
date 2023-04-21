from rest_framework.generics import RetrieveAPIView, ListCreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from django.contrib.auth import get_user_model

from main.serializers import RegisterSerializer, UserUpdateSerializer, UserSerializer, ProfileSerializer, \
    UserProfileSerializer, UpdateUserSerializer
from main.utils import otp_generator
from knox.models import AuthToken
from django.contrib.auth import login
from rest_framework import permissions, generics, status
import requests

User = get_user_model()


# Create your views here.

# class RegisterView(APIView):
#     @csrf_exempt
#     def post(self, request, format=None):
#         mobile = request.POST.get('mobile')
#
#         check_user = User.objects.filter(mobile=mobile).first()
#         check_profile = Profile.objects.filter(mobile=mobile).first()
#
#         if check_user or check_profile:
#             context = {'message': 'Mobile No. Already Exists!', 'class': 'danger'}
#             return Response(context, status=status.HTTP_400_BAD_REQUEST)
#
#         user = User.objects.create(username=mobile, mobile=mobile)
#         user.save()
#         otp = str(random.randint(999, 9999))
#         profile = Profile(user=user, mobile=mobile, otp=otp)
#         profile.save()
#         # send_otp(mobile, otp)
#         request.session['mobile'] = mobile
#         serializer = ProfileSerializer(profile)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


# @api_view(['POST'])
# def otp(request):
#     mobile = request.session.get('mobile')
#     if not mobile:
#         return Response({'message': 'Mobile number not found in session'}, status=status.HTTP_400_BAD_REQUEST)
#
#     otp = request.data.get('otp')
#     profile = Profile.objects.filter(mobile=mobile).first()
#
#     if not profile:
#         return Response({'message': 'Profile not found for the given mobile number'}, status=status.HTTP_404_NOT_FOUND)
#
#     if otp == profile.otp:
#         return Response({'message': 'OTP verification successful', "is_verified": True}, status=status.HTTP_200_OK)
#     else:
#         return Response({'message': 'Wrong OTP', "is_verified": False}, status=status.HTTP_401_UNAUTHORIZED)
#

# class LoginAttemptView(APIView):
#     def post(self, request):
#         mobile = request.POST.get('mobile')
#
#         user = Profile.objects.filter(mobile=mobile).first()
#
#         if user is None:
#             return Response({'message': 'User not found', 'class': 'danger'}, status=status.HTTP_400_BAD_REQUEST)
#
#         otp = str(random.randint(1000, 9999))
#         user.otp = otp
#         user.save()
#         send_otp(mobile, otp)
#         request.session['mobile'] = mobile
#         return Response(status=status.HTTP_302_FOUND)


# class LoginOtpView(APIView):
#     def get(self, request):
#         mobile = request.session['mobile']
#         context = {'mobile': mobile}
#         return Response(context)
#
#     def post(self, request):
#         mobile = request.session['mobile']
#         otp = request.data.get('otp')
#         profile = Profile.objects.filter(mobile=mobile).first()
#
#         if otp == profile.otp:
#             user = User.objects.get(id=profile.user.id)
#             login(request, user)
#             return Response(status=status.HTTP_302_FOUND)
#         else:
#             context = {'message': 'Wrong OTP', 'class': 'danger', 'mobile': mobile}
#             return Response(context, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            'response': serializer.data,
            'scucess': True,
            'message': 'User created successfully',
            'status': status.HTTP_201_CREATED,

        })


def send_otp(phone):
    """
    This is an helper function to send otp to session stored phones or
    passed phone number as argument.
    """

    if phone:

        key = otp_generator()
        phone = str(phone)
        otp_key = str(key)

        link = f'https://2factor.in/API/R1/?module=TRANS_SMS&apikey=7c59cf94-d129-11ec-9c12-0200cd936042&to={phone}&from=MMBook&templatename=mymedbook&var1={otp_key}&var2={otp_key}'

        result = requests.get(link, verify=False)

        return otp_key
    else:
        return False


class ValidatePhoneSendOTP(APIView):
    def post(self, request, *agrs, **kwargs):
        try:
            phone_number = request.data.get('phone')

            if phone_number:
                phone = str(phone_number)
                user = User.objects.filter(phone__iexact=phone)

                if user.exists():
                    data = user.first()
                    old_otp = data.otp
                    new_otp = send_otp(phone)
                    if old_otp:
                        data.otp = new_otp
                        data.save()
                        return Response({

                            'message': 'OTP sent successfully',
                            'status': status.HTTP_200_OK,
                        }, status=status.HTTP_200_OK)
                    else:
                        data.otp = new_otp
                        data.save()
                        return Response({
                            'message': 'OTP sent successfully',
                            'status': status.HTTP_200_OK,
                        },
                            status=status.HTTP_200_OK
                        )

                else:
                    return Response({
                        'message': 'User not found ! please register',
                        'status': status.HTTP_404_NOT_FOUND,
                    },
                        status=status.HTTP_400_BAD_REQUEST
                    )

            else:
                return Response({
                    'message': 'Phone number is required',
                    'status': status.HTTP_400_BAD_REQUEST,
                },
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            return Response({
                'message': str(e),
                'status': status.HTTP_400_BAD_REQUEST,
            },
                status=status.HTTP_400_BAD_REQUEST
            )


# verify otp
class VerifyPhoneOTPView(APIView):
    def post(self, request, format=None):
        # try:
        phone = request.data.get('phone')
        otp = request.data.get('otp')
        print(phone, otp)

        if phone and otp:
            user = User.objects.filter(phone__iexact=phone)
            if user.exists():
                user = user.first()
                if user.otp == otp:
                    login(request, user)
                    return Response({
                        'status': True,
                        'details': 'Login Successfully',
                        'token': AuthToken.objects.create(user)[1],
                        'response': {
                            'id': user.id,
                            # 'name': user.fname + ' ' + user.lname,
                            # 'email': user.email,
                            'phone': user.phone,
                            # 'address': user.address,
                            # 'city': user.city,
                        }})
                else:
                    return Response({'message': 'OTP does not match'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Phone or OTP is missing'}, status=status.HTTP_400_BAD_REQUEST)

        # except Exception as e:
        #     print(e)
        #     return Response({
        #         'status': False,
        #         'message': str(e),
        #         'details': 'Login Failed'
        #     })


# logout api view
class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        try:
            request.user.auth_token.delete()
            return Response({
                'message': 'Logout successfully',
                'status': status.HTTP_200_OK,
            })
        except Exception as e:
            return Response({
                'message': str(e),
                'status': status.HTTP_400_BAD_REQUEST,
            })


class UserRetrieveUpdateAPIView(APIView):
    # permission_classes = (IsAuthenticated,)
    serializer_class = UserUpdateSerializer

    def put(self, request, user_id, format=None):
        user = User.objects.get(id=user_id)
        serializer = UserUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class UserProfile(APIView):
#     def get(self, request):
#         serializer = UserProfileSerializer(self.request.user)
#         return Response(serializer.data)
#     # queryset = User.objects.all()
# serializer_class = UserProfileSerializer

class UserProfile(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

    def get_object(self):
        pk = self.kwargs.get('pk')

        if pk == "current":
            return self.request.user

        return super().get_object()


class UpdateProfileView(UpdateAPIView, ListAPIView):
    queryset = User.objects.all()
    # permission_classes = (IsAuthenticated,)
    serializer_class = UpdateUserSerializer
