from django.shortcuts import render

# Create your views here.


def login(request):#this function is used when user get in home page
    return render(request,'Page/login.html')