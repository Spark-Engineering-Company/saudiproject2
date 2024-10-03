from django.db import models


class User(models.Model):
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.full_name


class Food(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='foods/')
    contents = models.ManyToManyField('FoodContent', related_name='foods')

    def __str__(self):
        return self.name


class FoodContent(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class UserFoodSensitivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_content = models.ForeignKey(FoodContent, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.full_name  # Fixed the string representation


class ConfirmationLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    confirmed_at = models.DateTimeField(auto_now_add=True)
    result = models.BooleanField()  # True if no sensitivity, False if sensitivity
    sensitive_contents = models.ManyToManyField('FoodContent', related_name='confirmation_logs')

    def __str__(self):
        return self.user.full_name  # Fixed the string representation
