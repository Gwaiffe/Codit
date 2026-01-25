from django import forms
from .models import Topics, Entry


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topics
        fields = ['text', 'author']
        labels = {'text': 'Topic', 'author': 'Author'}


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['text']
        labels = {'text': ''}
        widgets = {'text': forms.Textarea(attrs={'cols': 100})}
