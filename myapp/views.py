from django.shortcuts import render
from myceleryproject.celery import add
from .tasks import sub
from celery.result import AsyncResult


# Create your views here.
# def index(request):
#     print("ok")
#     result = add.delay(10, 30)
#     print("result sum: ",result)
#     print("doing somthing")
#     result = sub.delay(40, 30)
#     print("result sub: ",result)
#     return render(request=request, template_name='myapp/home.html')

def index(request):
    result = add.delay(10, 30)
    return render(request=request, template_name='myapp/home.html', context={'result': result})


# Enqueue Task using apply_async()
def check_result(request, task_id):
    print("ok")
    result = AsyncResult(task_id)
    print('Ready: ', result.ready())
    print('Successful: ', result.successful())
    print('Failed: ', result.failed())

    return render(request=request, template_name='myapp/result.html', context={'result': result})



def about(request):
    return render(request=request, template_name='myapp/about.html')


def contact(request):
    return render(request=request, template_name='myapp/contact.html')