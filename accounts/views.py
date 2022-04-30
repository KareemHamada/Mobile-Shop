from django.shortcuts import render, redirect,HttpResponseRedirect
from .forms import SignupForm
from django.contrib.auth import authenticate, login
from django.contrib import messages


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            print(user)
            login(request, user) #
            return redirect('/')
        
        else:
            messages.error(request, 'Error in username , email or password')
            return redirect('/accounts/signup')
    else:
        form = SignupForm()
        return render(request, 'registration/signup.html', {"form": form})
