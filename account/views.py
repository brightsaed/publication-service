from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, UserProfileSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_class = permissions.AllowAny


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        return Response({
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        },
            status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_class = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        return Response(
            {'error': 'Use PATCH for partial updates'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def get_object(self):
        return self.request.user


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            outstanding_tokens = OutstandingToken.objects.filter(user=request.user)

            if outstanding_tokens.exists():
                latest_token = outstanding_tokens.order_by('-created_at').first()
                BlacklistedToken.objects.get_or_create(token=latest_token)

                return Response({
                    'detail': 'Выход выполнен успешно',
                })
            else:
                return Response({
                    'detail': 'Выход выполнен (активные сессии не найдены)'
                })

        except Exception as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )