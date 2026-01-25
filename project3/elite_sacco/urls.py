from django.urls import path
from . import views
app_name = 'elite_sacco'
urlpatterns = [path('', views.home_page, name='home_page'),
               path('members/', views.members, name='members'),
               path('savings/<int:members_id>/',
                    views.savings, name='savings'),
               ]
