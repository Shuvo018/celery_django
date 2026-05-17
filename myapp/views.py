from django.shortcuts import render
from myceleryproject.celery import add
from .tasks import sub



# Create your views here.
def index(request):
    print("ok")
    result = add.delay(10, 30)
    print("result sum: ",result)
    print("doing somthing")
    result = sub.delay(40, 30)
    print("result sub: ",result)
    return render(request=request, template_name='myapp/home.html')


def about(request):
    return render(request=request, template_name='myapp/about.html')


def contact(request):
    return render(request=request, template_name='myapp/contact.html')