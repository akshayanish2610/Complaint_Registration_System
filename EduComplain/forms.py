from django import forms
from django.contrib.auth.models import User
from .models import *
from django.core.exceptions import ValidationError


class StudentCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username','first_name','last_name', 'email', 'password', 'password2']

    
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['programme']


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['gender','date_of_birth',
                  'contact_number','address']

    widgets = {
        'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        
    }


class EditUserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['programme']

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['complaint_type', 'summary']

class ComplaintUpdateForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['status', 'comments']


#Staff Meeting
        
class StaffMeetingForm(forms.ModelForm):
    class Meta:
        model = StaffMeeting
        fields = ['title', 'description', 'meeting_datetime', 'google_meet_link']
            


