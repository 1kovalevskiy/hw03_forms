from django import forms
from .models import Group, Post
from django.contrib.auth import get_user_model


User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["text", "group"]
        # text = forms.CharField(widget=forms.Textarea)
        # group = forms.ModelChoiceField(queryset=Group.objects.all(), required=False)
        

class NewPostForm(PostForm):
    pass

class EditPostForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea)
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=False)