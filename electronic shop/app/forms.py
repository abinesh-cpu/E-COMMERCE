from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class UserRegistrationForm(UserCreationForm):
    phone = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'phone', 'address']

class CheckoutForm(forms.Form):
    address = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter your shipping address'}))
    payment_method = forms.ChoiceField(choices=[('credit_card', 'Credit Card'), ('paypal', 'PayPal')])