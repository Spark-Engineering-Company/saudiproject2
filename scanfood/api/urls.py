from django.urls import path
from rest_framework import permissions
from .views import UserCreateView, UserLoginView, FoodDetailView, ConfirmFoodView, UserFoodSensitivityView, FoodContentView, AddUserFoodSensitivityView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger Schema View
schema_view = get_schema_view(
   openapi.Info(
      title="Scan Food API",
      default_version='v1',
      description="API for Scan Food for Sensitivity",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@yourapi.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),  # Disable auth for the Swagger view

)
urlpatterns = [
    # User registration and login
    path('register/', UserCreateView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),

    # food details
    path('foods/<int:food_id>/', FoodDetailView.as_view()),

    # food check
    path('foods/<int:food_id>/confirm/', ConfirmFoodView.as_view()),

    # user sensitivity view
    path('users/<int:user_id>/food-sensitivities/', UserFoodSensitivityView.as_view()),

    # food contents view
    path('food-contents/', FoodContentView.as_view()),

    # add user sensitivities view
    path('users/<int:user_id>/food-sensitivities/add/', AddUserFoodSensitivityView.as_view())
]

