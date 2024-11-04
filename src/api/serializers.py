# from rest_framework import serializers
# from products.models import Product

# class ProductSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Product
#         fields = '__all__'
from rest_framework import serializers
from .models import CustomUser , RentalUnit, Feature # Import your custom user model

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'username', 'password', 'email', 'phoneNumber']

    def create(self, validated_data):
        user = CustomUser(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username'],
            email=validated_data['email'],
            phoneNumber=validated_data.get('phoneNumber'),
        )
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ['id', 'name']

class RentalUnitSerializer(serializers.ModelSerializer):
    features = serializers.ListField(child=serializers.CharField(), write_only=True)

    class Meta:
        model = RentalUnit
        fields = ['id', 'title', 'description', 'price', 'features', 'created_by', 'created_at']
        read_only_fields = ['created_by', 'created_at']
