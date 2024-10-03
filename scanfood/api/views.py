from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.hashers import make_password, check_password
from .serializers import *


# Utility function to format responses
def format_response(success, message, data=None, status_code=status.HTTP_200_OK):
    return Response({
        "success": success,
        "message": message,
        "data": data if data else {}
    }, status=status_code)


class UserCreateView(APIView):
    @swagger_auto_schema(
        operation_summary="Register a new user",
        request_body=UserSerializer,
        responses={
            200: 'User registered successfully',
            400: 'Bad Request - Validation error',
        }
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return format_response(True, "User created successfully.", UserSerializer(user).data, status.HTTP_201_CREATED)
        return format_response(False, "Error in creating user", serializer.errors, status.HTTP_400_BAD_REQUEST)


# User Login View based on phone + password
class UserLoginView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['phone'],
            properties={
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number'),
            },
        ),
        responses={
            200: openapi.Response('Login successful', UserSerializer),
            400: openapi.Response('Invalid login data'),
            404: openapi.Response('User not found'),
        },
    )
    def post(self, request):
        phone = request.data.get('phone')

        if not phone:
            return format_response(False, "Phone is required.", None)

        try:
            user = User.objects.get(phone=phone)
            serializer = UserSerializer(user)
            return format_response(True, "Login successful.", serializer.data)

        except User.DoesNotExist:
            return format_response(False, "User with this phone number not found.", None)


# Food Detail View
class FoodDetailView(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response('Food details', FoodSerializer),
            404: openapi.Response('Food not found'),
        },
    )
    def get(self, request, food_id):
        food = Food.objects.filter(id=food_id).first()
        if food:
            serializer = FoodSerializer(food)
            return format_response(200, 'Food details', serializer.data)
        return format_response(404, 'Food not found')


# Confirm Food Sensitivity View
class ConfirmFoodView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['user_id'],
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID'),
            },
        ),
        responses={
            201: openapi.Response(
                'Confirmation log created',
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'result': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Result'),
                        'sensitive_contents': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING, description='Sensitive contents')
                        )
                    }
                )
            ),
            400: openapi.Response('Invalid request'),
        },
    )
    def post(self, request, food_id):
        user_id = request.data.get('user_id')
        food = Food.objects.filter(id=food_id).first()
        user = User.objects.filter(id=user_id).first()

        if food and user:
            sensitive_contents = FoodContent.objects.filter(userfoodsensitivity__user=user)
            if sensitive_contents.filter(id__in=food.contents.all()).exists():
                result = False
                sensitive_contents_list = list(sensitive_contents.filter(id__in=food.contents.all()).values_list('name', flat=True))
            else:
                result = True
                sensitive_contents_list = []

            confirmation_log = ConfirmationLog.objects.create(user=user, food=food, result=result)
            confirmation_log.sensitive_contents.set(sensitive_contents)

            return format_response(201, 'Confirmation log created', {'result': result, 'sensitive_contents': sensitive_contents_list})

        return format_response(400, 'Invalid request')


# User's Food Sensitivities List
class UserFoodSensitivityView(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response('User food sensitivities', UserFoodSensitivitySerializer()),
            404: openapi.Response('User not found'),
        },
    )
    def get(self, request, user_id):
        # Fetch the user
        user = User.objects.filter(id=user_id).first()
        if user:
            # Collect all related food sensitivities for this user
            sensitivities = UserFoodSensitivity.objects.filter(user=user)

            # Extract the unique food content related to the user
            food_contents = {sensitivity.food_content for sensitivity in sensitivities}

            # Serialize the data
            user_data = UserSerializer(user).data
            food_content_data = FoodContentSerializer(food_contents, many=True).data

            # Create a single response object
            response_data = {
                'user': user_data,
                'food_content': food_content_data
            }

            return format_response(200, 'User food sensitivities', response_data)
        return format_response(404, 'User not found')


# List All Food Contents
class FoodContentView(APIView):
    @swagger_auto_schema(
        responses={
            200: openapi.Response('Food contents', FoodContentSerializer(many=True)),
        },
    )
    def get(self, request):
        contents = FoodContent.objects.all()
        serializer = FoodContentSerializer(contents, many=True)
        return format_response(200, 'Food contents', serializer.data)


# Add User Food Sensitivity
class AddUserFoodSensitivityView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['food_content_ids'],
            properties={
                'food_content_ids': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_INTEGER),
                    description='List of Food content IDs',
                ),
            },
        ),
        responses={
            201: openapi.Response('User food sensitivities added'),
            400: openapi.Response('Invalid request'),
        },
    )
    def post(self, request, user_id):
        user = User.objects.filter(id=user_id).first()
        food_content_ids = request.data.get('food_content_ids')

        if not user:
            return format_response(400, 'Invalid user')

        if not food_content_ids or not isinstance(food_content_ids, list):
            return format_response(400, 'Invalid request. food_content_ids should be a list')

        added_sensitivities = []
        for food_content_id in food_content_ids:
            food_content = FoodContent.objects.filter(id=food_content_id).first()
            if food_content:
                UserFoodSensitivity.objects.create(user=user, food_content=food_content)
                added_sensitivities.append(food_content_id)

        if added_sensitivities:
            return format_response(201, 'User food sensitivities added', {'added_food_content_ids': added_sensitivities})
        return format_response(400, 'No valid food content IDs found')
