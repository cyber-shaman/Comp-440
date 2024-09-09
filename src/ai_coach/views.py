from django.shortcuts import render



def home_view(request):
    return render(request, "home.html")

def signin(request):
    return render(request, "signin.html")

def survey(request):
    return render(request, "survey.html")
def success(request):
    return render(request, "success.html")

def register(request):
    return render(request,"signup.html")