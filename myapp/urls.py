
from django.urls import path
from myapp import views

urlpatterns = [
    path('', view=views.index, name='home'),
    path('about/', view=views.about, name='about'),
    path('contact/', view=views.contact, name='contact'),
]
