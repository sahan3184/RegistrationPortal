# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class SignupForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "role",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.update({
                "class": "w-full p-3 rounded-md border-2 border-gray-300 text-black focus:outline-none focus:ring-2 focus:ring-indigo-500"
            })
        self.fields["role"].widget.attrs.update({"class": "w-full p-3 rounded-md border-2 text-black"})
        self.fields["email"].required = False
