from django.shortcuts import render
from .models import Posts

# Create your views here.
def home(request):
    posts = Posts.objects.all()
    return render(request, "home.html", {"posts": posts})

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")

def post(request, pk):
    post = Posts.objects.get(id=pk)
    return render(request, "post.html", {"post":post})