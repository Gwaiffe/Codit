from django import forms
from .models import Posts, Comments


class UpdateForm(forms.ModelForm):
    class Meta:
        model = Posts
        fields = ['content', 'video', 'audio', 'image']
        labels = {'content': 'Content',
                  'video': 'Video', 'audio': 'Audio', 'image': 'Image'}
        widgets = {'content': forms.Textarea(attrs={'cols': 50, 'rows': 5})}


class PostForm(forms.ModelForm):
    class Meta:
        model = Posts
        fields = ['title', 'content', 'video', 'audio', 'image']
        labels = {'title': 'Title', 'content': 'Content',
                  'video': 'Video', 'audio': 'Audio', 'image': 'Image'}
        widgets = {'content': forms.Textarea(attrs={'cols': 50, 'rows': 5})}


class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['content',]
        labels = {'content': 'Comment'}
