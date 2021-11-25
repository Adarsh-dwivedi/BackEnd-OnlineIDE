from django.http import HttpResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from .models import Submission
from .serializer import UserSerializer, SubmissionSerializer
from .utils import create_file, execute_file
from django.contrib.auth import login
from django.contrib.auth.models import User

from rest_framework import permissions
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView

from multiprocessing import Process

# Create your views here.
def hello_world(request):
    return HttpResponse("Success")

@api_view(http_method_names=["POST"])
@permission_classes((permissions.AllowAny, ))
def register(request):
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response(UserSerializer(user).data, status=201)

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user).data, status=200)


class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super(LoginView, self).post(request, format=None)

class SubmissionViewSet(ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = queryset.filter(user=request.user)
        return Response(self.get_serializer(queryset, many=True).data, status=200)

    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data["status"] = "P"
        request.data["user"] = request.user.pk
        request.data._mutable = False

        serializer = SubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        submission = serializer.save()

        file_name = create_file(request.data.get("code"), request.data.get("language"))
        p = Process(target=execute_file, args=(file_name, request.data.get("language"), submission))
        p.start()

        return Response({
            "message": "Submitted Suceesfully"
        }, status=200)
