from . import views
from django.urls import path

app_name = 'admins'
urlpatterns = [path('index_page/', views.index_page, name='index'),
               path('new_member/', views.new_member, name='new_member'),
               path('new_save/<int:member_id>/',
                    views.new_save, name='new_save'),
               path('member/', views.member, name='member'),
               path('savings/<int:member_id>/',
                    views.saving, name='saving'),
               path('delete_member/<int:member_id>/',
                    views.delete_member, name='delete_member'),
               path('delete_save/<int:save_id>/',
                    views.delete_save, name='delete_save'),
               path('edit_member/<int:member_id>/',
                    views.edit_member, name='edit_member'),
               ]
