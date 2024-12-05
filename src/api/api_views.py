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
from django.shortcuts import render



from django.db import models  # For model-related functions like Max, Count

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

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import RentalUnit, Review
from .serializers import ReviewSerializer

@api_view(['POST'])
def submit_review(request):
    user = request.user
    today = timezone.now().date()

    # Extract rental_unit_id, rating, and description from the request data
    rental_unit_id = request.data.get('rental_unit_id')
    rating = request.data.get('rating')
    description = request.data.get('description')

    # Debugging: Log incoming data
    print("Incoming request data:", request.data)

    # Ensure all required fields are provided
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

    # Validate and save the review
    review_data = {
        'rental_unit': rental_unit.id,  # Use the ID of the rental unit
        'rating': rating,
        'description': description
    }
    serializer = ReviewSerializer(data=review_data)
    if serializer.is_valid():
        serializer.save(user=user, rental_unit=rental_unit)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        # Debugging: Log validation errors
        print("Validation errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
from django.db.models import Max

@api_view(['GET'])
def most_expensive_rental_units(request):
    features = request.GET.get('features', None)
    if features:
        feature_names = [name.strip() for name in features.split(',')]
        
        # Filter RentalUnit instances that contain all specified features
        rental_units = RentalUnit.objects.filter(
            features__name__in=feature_names
        ).distinct()

        # Further refine to include only units with all requested features
        for feature_name in feature_names:
            rental_units = rental_units.filter(features__name=feature_name)
        
        # Get the maximum price among the filtered units
        max_price = rental_units.aggregate(Max('price'))['price__max']
        
        # Filter only the most expensive units
        if max_price is not None:
            rental_units = rental_units.filter(price=max_price)
    else:
        # If no features are specified, return all rental units
        rental_units = RentalUnit.objects.all()

        # Get the maximum price among all units
        max_price = rental_units.aggregate(Max('price'))['price__max']
        
        # Filter only the most expensive units
        if max_price is not None:
            rental_units = rental_units.filter(price=max_price)

    serializer = RentalUnitSerializer(rental_units, many=True)
    print(serializer.data)
    return Response(serializer.data)






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


def most_rentals_on_date_view(request):
    return render(request, 'mostRentalsOnDate.html')

def reviews(request):
    return render(request, 'badReview.html')

def users_with_poor_reviews_view(request):
    return render(request, 'usersWithPoorReviews.html')  # Ensure the template exists

@api_view(['GET'])
def users_with_poor_reviews(request):
    users = CustomUser.objects.filter(
        review__rating='poor'
    ).exclude(
        review__rating__in=['excellent', 'good', 'fair']
    ).distinct()

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

def users_without_poor_reviews_view(request):
    return render(request,'greatHosts.html')

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



@api_view(['GET'])
def bad_reviews(request):
    # Get the review rating to filter from the query parameters
    rating = request.GET.get('rating', None)

    # Ensure a rating is provided
    if not rating:
        return Response({'error': 'Rating is required to search reviews.'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate the rating
    valid_ratings = ['excellent', 'good', 'fair', 'poor']
    if rating not in valid_ratings:
        return Response({'error': f"Invalid rating. Valid ratings are: {', '.join(valid_ratings)}."}, status=status.HTTP_400_BAD_REQUEST)

    # Filter reviews by rating
    reviews = Review.objects.filter(rating=rating).select_related('rental_unit', 'user', 'rental_unit__created_by')

    # Prepare response data
    data = []
    for review in reviews:
        rental_unit = review.rental_unit
        data.append({
            'title': rental_unit.title,
            'location': rental_unit.location,
            'description': rental_unit.description,
            'price': rental_unit.price,
            'review_description': review.description,
            'review_made_by': review.user.get_full_name() or review.user.username,
            'hosted_by': rental_unit.created_by.get_full_name() or rental_unit.created_by.username,
        })

    return Response(data, status=status.HTTP_200_OK)
from django.db.models import Q, Count



@api_view(['GET'])
def users_without_poor_reviews(request):
    # Exclude users who own rental units with "poor" reviews
    users = CustomUser.objects.exclude(
        rentalunit__reviews__rating='poor'
    ).annotate(
        review_count=Count('rentalunit__reviews')
    ).filter(review_count__gt=0)

    # Prepare response data
    data = []
    for user in users:
        rental_units = RentalUnit.objects.filter(created_by=user).prefetch_related('reviews')
        for rental_unit in rental_units:
            for review in rental_unit.reviews.all():
                data.append({
                    'user': user.get_full_name() or user.username,
                    'location': rental_unit.location or "N/A",
                    'description': rental_unit.description,
                    'review_description': review.description,
                    'rank': review.rating
                })

    return Response(data, status=status.HTTP_200_OK)

def user_units_with_positive_reviews_view(request):
    return render(request,'goodReviedUnits.html')
@api_view(['POST'])
def user_units_with_positive_reviews(request):
    user_id = request.data.get('user_id')

    if not user_id:
        return Response({'error': 'User ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Get the user
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Fetch rental units created by the user with reviews "Excellent" or "Good"
    rental_units = RentalUnit.objects.filter(
        created_by=user,
        reviews__rating__in=['excellent', 'good']
    ).distinct().prefetch_related('reviews')

    # Prepare response data
    data = []
    for rental_unit in rental_units:
        positive_reviews = rental_unit.reviews.filter(rating__in=['excellent', 'good'])
        for review in positive_reviews:
            data.append({
                'title': rental_unit.title,
                'location': rental_unit.location or "N/A",
                'description': rental_unit.description,
                'price': rental_unit.price,
                'review_description': review.description,
                'rank': review.rating,
                'reviewed_by': review.user.get_full_name() or review.user.username,
            })

    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_users_with_units(request):
    # Fetch all users who have hosted at least one rental unit
    users = CustomUser.objects.filter(rentalunit__isnull=False).distinct()

    # Prepare response data
    data = [
        {
            'id': user.id,
            'name': user.get_full_name() or user.username
        }
        for user in users
    ]

    return Response(data, status=status.HTTP_200_OK)
