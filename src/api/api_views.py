from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .models import CustomUser

@api_view(['POST'])
def api_signup(request):

    data = request.data  # This contains the JSON sent from the frontend
    print(data)    
    # Check if passwords match
    if data.get('password') != data.get('confirm_password'):
        return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if email or username already exists
    if CustomUser.objects.filter(email=data.get('email')).exists():
        return Response({'error': 'Email is already in use'}, status=status.HTTP_400_BAD_REQUEST)
    if CustomUser.objects.filter(username=data.get('username')).exists():
        return Response({'error': 'Username is already in use'}, status=status.HTTP_400_BAD_REQUEST)
    if CustomUser.objects.filter(phoneNumber=data.get('phoneNumber')).exists():
        return Response({'error': 'Phone number is already in use'}, status=status.HTTP_400_BAD_REQUEST)
    # Serialize and validate the input data
    serializer = UserSerializer(data=data)
    if serializer.is_valid():
        user = serializer.save()  # This saves the user with the hashed password
        user.set_password(data.get('password'))  # Ensure the password is hashed
        user.save()

        # Create and return a token if you're using token authentication
        token = Token.objects.create(user=user)
        return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #return Response("User created successfully", status=status.HTTP_201_CREATED)


@api_view(['POST'])
def api_login(request):
    data = request.data
    email = data.get('email')
    password = data.get('password')

    # Check if email exists in the CustomUser model
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return Response({'error': "Gmail doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)

    # Check if password is correct
    user = authenticate(request, username=user.username, password=password)
    
    if user is not None:
        # Authentication successful, generate or retrieve the token
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': user.username}, status=status.HTTP_200_OK)
    else:
        # Email exists, but password is incorrect
        return Response({'error': 'Password is not correct'}, status=status.HTTP_400_BAD_REQUEST)