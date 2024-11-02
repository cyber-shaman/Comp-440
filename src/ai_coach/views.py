from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages

def home_view(request):
    return render(request, "home.html")

def signin_view(request):
    return render(request, "signin.html")

def signup_view(request):
    return render(request, "signup.html")


def survey(request):
    return render(request, "survey.html")

def account_created(request):
    return render(request, "account_created.html")

def bookRoom(request):
    return render(request, "bookRoom.html")

def hostRoom(request):
    return render(request, "hostRoom.html")