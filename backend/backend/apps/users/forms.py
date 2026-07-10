from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """
    A form for creating new users in the Django Admin.
    Uses email as the primary identification field instead of username.
    """
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'first_name', 'last_name', 'role')

    def clean_email(self):
        """
        Validate that the email address is unique.
        """
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                _("A user with that email already exists."),
                code='unique_email',
            )
        return email

class CustomUserChangeForm(UserChangeForm):
    """
    A form for updating existing users in the Django Admin.
    """
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'
