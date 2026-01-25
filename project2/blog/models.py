from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Posts(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    video = models.FileField(
        upload_to='videos/', blank=True, null=True)
    audio = models.FileField(
        upload_to='audio/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if len(self.content) > 50:
            return f'{self.content[:50]}...'
        else:
            return f'{self.content}'

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'


class Comments(models.Model):
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)
    content = models.CharField(max_length=300, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.content}'

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
