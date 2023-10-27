from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
from .serializers import CustomUserSerializer
from django.contrib.auth.hashers import make_password
from django.shortcuts import render
import cv2
from django.http import StreamingHttpResponse, HttpResponseServerError
from django.views.decorators import gzip

class CustomUserAPIView(APIView):
    def post(self, request, format=None):
        data=request.data.copy()
        data['password']=make_password(data['password'])
        serializer = CustomUserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Registration successful"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def signup(request):
    return render(request, 'signup.html')

def test(request):
    return render(request, 'test.html')

def fail(request):
    return render(request, 'fail.html')

def complete(request):
    return render(request, 'complete.html')

@gzip.gzip_page
def stream_camera(request):
    try:
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            raise RuntimeError("Could not start camera.")

        def generate():
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                _, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        response = StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')

    except RuntimeError as e:
        response = HttpResponseServerError(str(e))

    return response