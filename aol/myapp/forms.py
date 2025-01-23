from django import forms

class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=100, 
        required=True, 
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}), 
        required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}), 
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        # Check if the password and confirm password match
        if password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')

        return cleaned_data
    
class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=100, 
        required=True, 
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}), 
        required=True
    )