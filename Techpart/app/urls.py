from django.urls import path
from . import views
urlpatterns=[
    path('',views.index),
    path('about',views.about),
    path('contact',views.contact),
    path('login',views.login),
    path('register',views.register)
]