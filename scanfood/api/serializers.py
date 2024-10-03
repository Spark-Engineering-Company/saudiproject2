from rest_framework import serializers
from .models import User, Food, FoodContent, UserFoodSensitivity, ConfirmationLog


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'phone']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ['id', 'name', 'image', 'contents']


class FoodContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodContent
        fields = ['id', 'name']


class UserFoodSensitivitySerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Include full user details
    food_content = serializers.SerializerMethodField()  # Custom method to gather food items

    class Meta:
        model = UserFoodSensitivity
        fields = ['user', 'food_content']  # Adjust as needed

    def get_food_content(self, obj):
        # Retrieve all related food_content for this user
        user_food_sensitivities = UserFoodSensitivity.objects.filter(user=obj.user)
        food_contents = [sensitivity.food_content for sensitivity in user_food_sensitivities]
        return FoodContentSerializer(food_contents, many=True).data


class ConfirmationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfirmationLog
        fields = ['id', 'user', 'food', 'confirmed_at', 'result', 'sensitive_contents']
