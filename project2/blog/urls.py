from django.urls import path
from . import views

app_name = 'blog'
urlpatterns = [path('', views.home_page, name='home_page'),
               path('posts/', views.post, name='posts'),
               path('add_post/', views.add_post, name='add_post'),
               path('update_post/<int:post_id>/',
                    views.update_post, name='update_post'),
               path('submit_comments/<int:post_id>/',
                    views.submit_comment, name='submit_comment'),
               path('comments/<int:post_id>/',
                    views.comment, name='comments'),
               ]
