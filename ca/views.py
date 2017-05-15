from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'ca/index.html')

def has_root_key(request):
    return  render(request, 'ca/has_root_key.html')

def no_root_key(request):
    return  render(request, 'ca/no_root_key.html')

def login_page(request):
    return render(request, 'ca/login_page.html')