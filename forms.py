from django import forms
from .models import Post, Comment
from captcha.fields import ReCaptchaField

class PostForm(forms.ModelForm):
    title = forms.CharField(max_length=128)
    body = forms.CharField(max_length=245, label="Item Description.")

    class Meta:
        model = Post
        fields = ('title', 'body', )

class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=30)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)

class CommentForm(forms.ModelForm):
    captcha = ReCaptchaField()
    body = forms.CharField(label="", widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Text goes here!!!', 'rows':'4', 'cols': '50'}))


    class Meta:
        model = Comment
        fields = ('name', 'email', 'body',)

class SearchForm(forms.Form):
    query = forms.CharField()


class ContactForm(forms.Form):
    name = forms.CharField(max_length=250)
    company = forms.CharField(max_length=250)
    email = forms.EmailField()
    to = forms.EmailField()
    phone_numner = forms.IntegerField()
    message = forms.CharField(widget=forms.Textarea)

class SubscriberForm(forms.Form):
    email = forms.EmailField(max_length=100,
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))
    
    

