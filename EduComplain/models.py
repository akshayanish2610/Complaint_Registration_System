
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    programme = models.CharField(max_length=40)
    is_staff = models.BooleanField(default=False)

    
class StudentProfile(models.Model):
    student=models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Complaint(models.Model):
    COMPLAINT_TYPES = (
        ('about_college', 'About College'),
        ('about_dept', 'About Dept'),
        ('about_staff', 'About Staff'),
    )

    COMPLAINT_STATUS = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('ongoing', 'Ongoing'),
        ('solved', 'Solved'),
    )

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='register_complaints')
    complaint_type = models.CharField(max_length=15, choices=COMPLAINT_TYPES, default='about_college')
    summary = models.TextField()
    status = models.CharField(max_length=10, choices=COMPLAINT_STATUS, default='pending')
    accepter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='accepted_complaints')
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    report = models.FileField(upload_to='complaint_reports/', null=True, blank=True)  # Add this line for the report field

    def __str__(self):
        return f"{self.student.username}'s complaint"

    


#Staff Meeting 
class StaffMeeting(models.Model):
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='staff_meetings')
    title = models.CharField(max_length=100)
    description = models.TextField()
    meeting_datetime = models.DateTimeField()
    google_meet_link = models.URLField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_expired = models.BooleanField(default=False)

    def __str__(self):
        return self.title