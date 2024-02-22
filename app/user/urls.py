"""
URLS MAPPING FOR THE USER API
"""

from django.urls import path
from . import views

app_name = 'user'  # define for the reverse mapping for the testing user api in instance CREATE_USER_URL

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),  # that is used for the reverse lookup user:create
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
]
