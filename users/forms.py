# from django import forms
# from django.contrib.auth.models import User
#
#
# class RegistrationForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput)
#     password2 = forms.CharField(widget=forms.PasswordInput)
#
#     class Meta:
#         model = User
#         fields = ["username"]
#
#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get("password")
#         password2 = cleaned_data.get("password2")
#
#         if password != password2:
#             raise forms.ValidationError("Пароли не совпадают")
#
#         return cleaned_data
#
#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data["password"])
#
#         if commit:
#             user.save()
#
#         return user