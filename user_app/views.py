from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
from .serializers import CustomUserSerializer
from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from datetime import datetime
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
    sign_up_date = datetime.now().strftime("%Y-%m-%d")
    return render(request, 'complete.html', {'sign_up_date': sign_up_date})

@gzip.gzip_page
def stream_camera(request):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    face_detected = False
    frame_count = 0

    try:
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            raise RuntimeError("Could not start camera.")

        def generate():
            nonlocal face_detected, frame_count
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_count += 1
                if frame_count % 10 == 0:  # Run face detection every 10 frames
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

                    if len(faces) > 0 and not face_detected:
                        face_detected = True
                    elif len(faces) == 0 and face_detected:
                        print("Face gone out of the camera")
                        face_detected = False

                _, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        response = StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')

    except RuntimeError as e:
        response = HttpResponseServerError(str(e))

    return response