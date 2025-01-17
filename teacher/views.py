from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from teacher.serializers import TeacherLoginSerializer
from rest_framework.views import APIView 
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from admins.utilities.token import get_tokens_for_user
from admins.models import User , Role
from rest_framework.permissions import IsAuthenticated
import logging
from .models import Teacher, ClassRoomTeacher , ClassRoom
from .serializers import ClassRoomSerializer ,StudentSerializer , StudentBusServiceSerializer
from student.models import Student , StudentBusService

logger = logging.getLogger(__name__)


class TeacherLoginAPIView(APIView):
    def post(self, request):
      serializer = TeacherLoginSerializer(data=request.data)
      try:
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
              login(request, user)
              token = get_tokens_for_user(user)
              return Response(
                  {'message': 'Login successful', 'token':token}, 
                  status=status.HTTP_200_OK
              )
            logger.warning("User authentication failed: No user found with provided credentials.")
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      except Exception as e:
            logger.exception("An error occurred during user authentication:")
            return Response({'message': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
          
          


class TeacherClassStudentsAPIView(APIView):
    
    def get(self, request):
        user = request.user
        try:
            teacher = Teacher.objects.get(user=user)
        except Teacher.DoesNotExist:
            return Response({"error": "Teacher not found."}, status=status.HTTP_404_NOT_FOUND)

        class_rooms = ClassRoom.objects.filter(
            classroom_teachers__teacher=teacher, 
            classroom_teachers__is_class_teacher=True
        )
        
        if not class_rooms.exists():
            return Response({"error": "No class assigned to this teacher."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ClassRoomSerializer(class_rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
      
      
      
class TeacherBusStudentsAPIView(APIView):
  
    def get(self,request):
        user = request.user
        
        try:
            teacher = Teacher.objects.get(user=user)
        except:
            return Response({"error": "Teacher not found."}, status=status.HTTP_404_NOT_FOUND)
          
        classrooms = ClassRoom.objects.filter(classroom_teachers__teacher=teacher, classroom_teachers__is_class_teacher=True)

        if not classrooms.exists():
            return Response({"error": "No class assigned to this teacher."}, status=status.HTTP_404_NOT_FOUND)
        
        students = Student.objects.filter(classRoom__in=classrooms, is_bus=True)

        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentBusServiceAPIView(APIView):

    def get(self, request, student_id):
      
        classroom = ClassRoom.objects.filter(teachers__user=request.user).first()
        try:
            student = Student.objects.get(user_id=student_id, is_bus=True, classRoom=classroom)
            bus_service = student.bus_service
        except Student.DoesNotExist:
            return Response(
              {"error": "Student not found or not using bus."},
              status=status.HTTP_404_NOT_FOUND
            )
        except StudentBusService.DoesNotExist:
            return Response(
              {"error": "Bus service for student not found."}, 
              status=status.HTTP_404_NOT_FOUND
            )

        serializer = StudentBusServiceSerializer(bus_service)
        return Response({"data":serializer.data}, status=status.HTTP_200_OK)
      
      
    def put(self,request,student_id):
        classroom = ClassRoom.objects.filter(teachers__user=request.user).first()
        try:
            student = Student.objects.get(user_id=student_id, is_bus=True, classRoom=classroom)
            bus_service = student.bus_service
        except Student.DoesNotExist:
            return Response(
              {"error": "Student not found or not using bus."},
              status=status.HTTP_404_NOT_FOUND
            )
        except StudentBusService.DoesNotExist:
            return Response(
              {"error": "Bus service for student not found."}, 
              status=status.HTTP_404_NOT_FOUND
            )
            
        payment = request.data.get('payment')
        
        try:
            payment = float(payment)
            if payment < 0:
                return Response({"error": "Payment amount cannot be negative."}, status=status.HTTP_400_BAD_REQUEST)
            
            bus_fees = bus_service.annual_fees - payment
            if bus_fees < 0:
                bus_fees = 0  
            
            bus_service.annual_fees = bus_fees
            bus_service.save()
            
            serializer = StudentBusServiceSerializer(bus_service)
            return Response({"data": serializer.data,"msg":"Bus Fees paid successfully"}, status=status.HTTP_200_OK)
        
        except ValueError:
            return Response({"error": "Invalid payment amount."}, status=status.HTTP_400_BAD_REQUEST)
          
        