# from rest_framework import serializers
# from products.models import Product

# class ProductSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Product
#         fields = '__all__'
from rest_framework import serializers
from .models import CustomUser , RentalUnit, Feature, RentalUnitFeature, Review# Import your custom user model

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


# class RentalUnitSerializer(serializers.ModelSerializer):
#     created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
#     features = FeatureSerializer(many=True, read_only=True)  # Read-only features for output
#     feature_names = serializers.ListField(
#         child=serializers.CharField(),
#         write_only=True,
#         required=False
#     )  # Write-only field for feature names during creation

#     class Meta:
#         model = RentalUnit
#         fields = ['id', 'title', 'description', 'price', 'features', 'feature_names', 'created_by_name', 'created_at']
#         read_only_fields = ['created_by', 'created_at']

#     def create(self, validated_data):
#         features_data = validated_data.pop('feature_names', [])  # Retrieve the list of feature names
#         rental_unit = RentalUnit.objects.create(**validated_data)

#         for feature_name in features_data:
#             feature, created = Feature.objects.get_or_create(name=feature_name)
#             RentalUnitFeature.objects.create(rental_unit=rental_unit, feature=feature)

#         return rental_unit
class RentalUnitSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    features = FeatureSerializer(many=True, read_only=True)  # Read-only features for output
    feature_names = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )  # Write-only field for feature names during creation

    class Meta:
        model = RentalUnit
        fields = ['id', 'title', 'location', 'description', 'price', 'features', 'feature_names', 'created_by_name', 'created_at']
        read_only_fields = ['created_by', 'created_at']

    def create(self, validated_data):
        features_data = validated_data.pop('feature_names', [])  # Retrieve the list of feature names
        rental_unit = RentalUnit.objects.create(**validated_data)

        for feature_name in features_data:
            feature, created = Feature.objects.get_or_create(name=feature_name)
            RentalUnitFeature.objects.create(rental_unit=rental_unit, feature=feature)

        return rental_unit




class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'rental_unit', 'user', 'rating', 'description', 'created_at']
        read_only_fields = ['user', 'created_at']