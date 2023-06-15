from django import forms
from django.contrib.auth.forms import UserCreationForm
from orders.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(max_length=30, required=True)
    company = forms.CharField(max_length=100, required=True)
    position = forms.CharField(max_length=100, required=True)
    password1 = forms.CharField(max_length=100, widget=forms.PasswordInput(), label="Password")
    password2 = forms.CharField(max_length=100, widget=forms.PasswordInput(), label="Confirm password")

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'company', 'position', 'password1', 'password2')

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        user.company = self.cleaned_data['company']
        user.position = self.cleaned_data['position']
        if commit:
            user.save()
        return user