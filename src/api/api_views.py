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
from .models import RentalUnit, Feature, RentalUnitFeature, RentalLimit , Review
from .serializers import RentalUnitSerializer, FeatureSerializer , ReviewSerializer 




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
        
        # Increment the daily count
        rental_limit.count += 1
        rental_limit.save()

        # Return the serialized data of the created rental unit
        return Response(RentalUnitSerializer(rental_unit).data, status=status.HTTP_201_CREATED)
    else:
        print("Validation errors:", serializer.errors)  # Debugging: print validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['GET'])
def get_rental_units(request):
    features = request.GET.get('features', None)
    if features:
        feature_names = [name.strip() for name in features.split(',')]
        
        # Filter RentalUnit instances that contain all specified features
        rental_units = RentalUnit.objects.filter(
            features__name__in=feature_names
        ).distinct()

        # Filter to include only units with all requested features
        for feature_name in feature_names:
            rental_units = rental_units.filter(features__name=feature_name)

    else:
        rental_units = RentalUnit.objects.all()

    serializer = RentalUnitSerializer(rental_units, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def submit_review(request):
    user = request.user
    today = timezone.now().date()

    # Extract rental_unit_id from request data
    rental_unit_id = request.data.get('rental_unit_id')
    rating = request.data.get('rating')
    description = request.data.get('description')

    # Ensure rental_unit_id, rating, and description are provided
    if not rental_unit_id or not rating or not description:
        return Response({'error': 'rental_unit_id, rating, and description are required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Get the rental unit
    try:
        rental_unit = RentalUnit.objects.get(id=rental_unit_id)
    except RentalUnit.DoesNotExist:
        return Response({'error': 'Rental unit not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Constraint 1: No self-reviews
    if rental_unit.created_by == user:
        return Response({'error': 'You cannot review your own rental unit.'}, status=status.HTTP_400_BAD_REQUEST)

    # Constraint 2: Maximum 3 reviews per day
    daily_reviews = Review.objects.filter(user=user, created_at__date=today).count()
    if daily_reviews >= 3:
        return Response({'error': 'You can only submit up to 3 reviews per day.'}, status=status.HTTP_400_BAD_REQUEST)

    # Constraint 3: Only one review per rental unit
    if Review.objects.filter(rental_unit=rental_unit, user=user).exists():
        return Response({'error': 'You have already reviewed this rental unit.'}, status=status.HTTP_400_BAD_REQUEST)

    # Create and save the review
    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=user, rental_unit=rental_unit)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        print("Validation errors:", serializer.errors)  # Debugging: print validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)