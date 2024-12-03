from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import RentalUnit, Feature, RentalUnitFeature, RentalLimit
from .serializers import RentalUnitSerializer, FeatureSerializer


from django.db import models  # For model-related functions like Max, Count
from django.shortcuts import render  # For rendering templates
from rest_framework.response import Response  # For API responses
from rest_framework.decorators import api_view  # For defining API views
from rest_framework import status  # For HTTP status codes
from .models import Review, CustomUser  # Import your models


from .models import CustomUser

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import CustomUser
from .serializers import UserSerializer
from django.contrib.auth import authenticate

@api_view(['POST'])
def api_signup(request):
    data = request.data

    # Validate password match
    if data.get('password') != data.get('confirm_password'):
        return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if email, username, or phone number already exist
    if CustomUser.objects.filter(email=data.get('email')).exists():
        return Response({'error': 'Email is already in use'}, status=status.HTTP_400_BAD_REQUEST)
    if CustomUser.objects.filter(username=data.get('username')).exists():
        return Response({'error': 'Username is already in use'}, status=status.HTTP_400_BAD_REQUEST)
    if CustomUser.objects.filter(phoneNumber=data.get('phoneNumber')).exists():
        return Response({'error': 'Phone number is already in use'}, status=status.HTTP_400_BAD_REQUEST)

    # Serialize and validate data
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        user = serializer.save()
        user.set_password(data.get('password'))  # Ensure the password is hashed
        user.save()

        # Create token for the user
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework.response import Response
# from rest_framework.decorators import api_view

# @api_view(['POST'])
# def api_login(request):
#     # Authenticate user (check credentials)
#     # If valid, generate a token
#     user = authenticate(request, email=request.data['email'], password=request.data['password'])
#     if user is not None:
#         refresh = RefreshToken.for_user(user)
#         response = Response({
#             'message': 'Login successful'
#         })
#         # Set the token as an HttpOnly cookie
#         response.set_cookie('access', str(refresh.access_token), httponly=True)
#         response.set_cookie('refresh', str(refresh), httponly=True)
#         return response
#     else:
#         return Response({'error': 'Invalid credentials'}, status=400)


@api_view(['POST'])
def api_login(request):
    data = request.data
    email = data.get('email')
    password = data.get('password')

    # Check if the email exists in the CustomUser model
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return Response({'error': "Email doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)

    # Authenticate user by username and password
    user = authenticate(request, username=user.username, password=password)
    
    if user is not None:
        # Authentication successful, create or retrieve the token
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': user.username}, status=status.HTTP_200_OK)
    else:
        # Email exists, but password is incorrect
        return Response({'error': 'Password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
##@permission_classes([IsAuthenticated])
def add_rental_unit(request):
    user = request.user
    today = timezone.now().date()
    
    # Check daily post limit
    rental_limit, created = RentalLimit.objects.get_or_create(user=user, date=today)
    if rental_limit.count >= 2:
        return Response({'error': 'You can only post 2 rental units per day.'}, status=status.HTTP_400_BAD_REQUEST)

    # Deserialize and validate data
    serializer = RentalUnitSerializer(data=request.data)
    if serializer.is_valid():
        rental_unit = serializer.save(created_by=user)
        
        # Handle features
        feature_names = serializer.validated_data['features']
        for name in feature_names:
            feature, _ = Feature.objects.get_or_create(name=name)
            RentalUnitFeature.objects.create(rental_unit=rental_unit, feature=feature)
        
        # Increment the daily count
        rental_limit.count += 1
        rental_limit.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_rental_units(request):
    query = request.GET.get('feature', None)
    if query:
        rental_units = RentalUnit.objects.filter(rentalunitfeature__feature__name__icontains=query).distinct()
    else:
        rental_units = RentalUnit.objects.all()
    
    serializer = RentalUnitSerializer(rental_units, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def most_expensive_rental_units(request):
    rental_units = (
        RentalUnit.objects
        .annotate(max_price=models.Max('price'))
        .values('id', 'title', 'price')
    )
    return Response(rental_units, status=status.HTTP_200_OK)

@api_view(['GET'])
def users_posted_two_rentals_with_features(request):
    feature_x = request.GET.get('feature_x')
    feature_y = request.GET.get('feature_y')

    rentals = RentalUnit.objects.filter(
        rentalunitfeature__feature__name__in=[feature_x, feature_y]
    ).values('created_by', 'created_at')

    return Response(rentals, status=status.HTTP_200_OK)

@api_view(['GET'])
def rentals_with_positive_reviews(request):
    user_id = request.GET.get('user_id')  # Get the user ID from the request
    rentals = RentalUnit.objects.filter(
        created_by_id=user_id,
        reviews__rating__in=['excellent', 'good']
    ).exclude(reviews__rating__in=['fair', 'poor']).distinct()

    serializer = RentalUnitSerializer(rentals, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def most_rentals_on_date(request):
    date = '2024-10-15'  # Hardcoded for the example; can be made dynamic
    rentals = RentalUnit.objects.filter(
        created_at__date=date
    ).values('created_by').annotate(count=models.Count('id')).order_by('-count')

    max_count = rentals[0]['count'] if rentals else 0
    top_users = [rental['created_by'] for rental in rentals if rental['count'] == max_count]

    return Response({'top_users': top_users, 'max_count': max_count}, status=status.HTTP_200_OK)

@api_view(['GET'])
def users_with_only_poor_reviews(request):
    users = CustomUser.objects.filter(
        reviews__rating='poor'
    ).exclude(reviews__rating__in=['excellent', 'good', 'fair']).distinct()

    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def users_with_no_poor_reviews(request):
    users = CustomUser.objects.exclude(
        rentalunit__reviews__rating='poor'
    ).filter(rentalunit__isnull=False).distinct()

    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

def most_expensive_rentals_view(request):
    return render(request, 'mostExpensive.html')

def rentals_with_features_view(request):
    feature_x = request.GET.get('feature_x', '')
    feature_y = request.GET.get('feature_y', '')
    
    # Query the database based on the features entered
    rentals = RentalUnit.objects.filter(
        rentalunitfeature__feature__name__in=[feature_x, feature_y]
    ).distinct()
    
    context = {
        'results': rentals,  # Passing the search results
    }
    
    return render(request, 'twoRentalsWithFeatures.html', context)