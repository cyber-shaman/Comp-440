from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import render
#from .serializers import ProductSerializer


from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

#from api.utility import make_openAI_request

import requests
import json
import os
from openai import OpenAI
#client = OpenAI(api_key=os.environ['OPENAI_SECRET_KEY'])
# @api_view(['GET'])
# def get_Data(request):
#     #person = {'name':'danis'}
#     products = Product.objects.all()
#     serializer = ProductSerializer(products, many=True)

#     return Response(serializer.data)



from .serializers import UserSerializer

@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({'token': token.key, 'user': serializer.data})
    return Response(serializer.errors, status=status.HTTP_200_OK)

@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response("missing user", status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(user)
    return Response({'token': token.key, 'user': serializer.data})

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response("passed!")



@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def subscriptionStatus(request):
    #Do logic here for accoutn subscription using the stripe account
    return Response("no SubscriptinStatus yet")

@api_view(['POST'])
def receiveData(request):
    Age = request.data['Age']
    Gender = request.data['Gender']
    Current_weight = request.data['Current_weight']
    Desired_weight = request.data['Desired_weight']
    Diet_restrictions = request.data['Diet_restrictions']
    Disliked_Foods = request.data['Disliked_Foods']
    Preferred_food = request.data['Preferred_food']
    Health_conditions = request.data['Health_conditions']
    Weekly_budget = request.data['Weekly_budget']
    extra_information = request.data['extra_information']
    exercise_frequency = request.data['exercise_frequency']
    print(Age)
    response = dietGenerator(Age,Gender,Current_weight,Desired_weight,Diet_restrictions,Disliked_Foods,Preferred_food,Health_conditions,Weekly_budget,extra_information,exercise_frequency)
    print(response)
    return Response(response)

def dietGenerator(Age,Gender,Current_weight,Desired_weight,Diet_restrictions,Disliked_Foods,Preferred_food,Health_conditions,Weekly_budget,extra_information,exercise_frequency):
    system_prompt = """You are an expert in designing flow diagrams for applications. Generate a JSON object that represents nodes and edges for a flow hierarchical diagram, top-down. The JSON should include two arrays: "nodes" and "edges".
1. **Nodes Array**:
   - Each node should have the following properties:
     - `id`: A unique identifier for the node (string).
     - `position`: An object specifying the `x` and `y` coordinates for the node's position (integers).
     - `data`: An object containing a `label` property, which is a string representing the name or label of the node.
   Example node format:
   ```json
   {
     "id": "1",
     "position": { "x": 0, "y": 0 },
     "data": { "label": "Node 1" }
   }
   ```
2. **Edges Array**:
   - Each edge should have the following properties:
     - `id`: A unique identifier for the edge (string).
     - `source`: The id of the source node (string).
     - `target`: The id of the target node (string).
   Example edge format:
   ```json
   {
     "id": "e1-2",
     "source": "1",
     "target": "2"
   }
   ```
Example Output Structure: The JSON object should be structured as follows:
{
  "nodes": [
    {
      "id": "1",
      "position": { "x": 0, "y": 0 },
      "data": { "label": "Node 1" }
    },
    {
      "id": "2",
      "position": { "x": 150, "y": 100 },
      "data": { "label": "Node 2" }
    }
  ],
  "edges": [
    {
      "id": "e1-2",
      "source": "1",
      "target": "2"
    }
  ]
}
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": system_prompt
        }],
        temperature=0.8,
        max_tokens=1000
    )
    content = response.choices[0].message.content
    data = content.strip()

    return data

