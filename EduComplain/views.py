from io import BytesIO
from pyexpat.errors import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from .models import Complaint, StudentProfile, UserProfile
from django.template.loader import get_template
from xhtml2pdf import pisa

from EduComplain.forms import ComplaintForm, ComplaintUpdateForm, EditUserProfileForm, StudentCreationForm, StudentProfileForm, UserProfileForm, UserUpdateForm
from .models import UserProfile

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            user_profile = UserProfile.objects.get(user=user)
            
            if user_profile.is_staff:
                return redirect('staff_dashboard')
            else:
                return redirect('student_dashboard')
        else:
            error_message = 'Invalid login credentials'
            return render(request, 'login.html', {'error': error_message})
    else:
        return render(request, 'login.html')
    

@login_required
def user_logout(request):
    logout(request)
    return redirect('user_login')
from django.contrib.auth.decorators import login_required, user_passes_test
    

from .models import StaffMeeting

@login_required(login_url='/')  
def staff_dashboard(request):
    # Fetch the recent 3 complaints
    recent_complaints = Complaint.objects.order_by('-created_at')[:3]

    # Fetch staff details
    staff_details = UserProfile.objects.filter(is_staff=True)

    # Fetch staff meetings (limit to 4 most recent, exclude expired meetings)
    staff_meetings = StaffMeeting.objects.filter(staff=request.user).order_by('-created_at')[:4]

    # Check and mark meetings as expired
    current_datetime = timezone.now()
    for meeting in staff_meetings:
        if meeting.meeting_datetime < current_datetime:
            meeting.is_expired = True
        else:
            meeting.is_expired = False

    # Exclude expired meetings from the queryset
    staff_meetings = [meeting for meeting in staff_meetings if not meeting.is_expired]

    context = {
        'recent_complaints': recent_complaints,
        'staff_details': staff_details,
        'staff_meetings': staff_meetings,
    }

    return render(request, 'staff_dashboard.html', context)




@login_required(login_url='/')  
def student_dashboard(request):
    # Retrieve the most recent 5 complaints
    recent_complaints = Complaint.objects.filter(student=request.user).order_by('-created_at')[:3]

    # Get the details of the latest complaint
    latest_complaint = recent_complaints.first()

    # Fetch staff details (you need to define the correct query to get the staff details)
    staff_details = UserProfile.objects.filter(is_staff=True) 
    print(staff_details)  

    return render(request, 'student_dashboard.html', {'recent_complaints': recent_complaints, 'latest_complaint': latest_complaint, 'staff_details': staff_details})


    

from django.contrib.auth import authenticate, login

def create_student(request):
    if request.method == 'POST':
        user_form = StudentCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            # Save the user form data
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            # Save the profile form data
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            # Do not log in the user automatically
            # Remove the following lines:
            # user = authenticate(request, username=user_form.cleaned_data['username'], password=user_form.cleaned_data['password'])
            # login(request, user)

            return redirect('student_list')  # Change to the desired URL for the staff dashboard

    else:
        user_form = StudentCreationForm()
        profile_form = UserProfileForm()

    return render(request, 'create_student.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
def student_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    
    try:
        student_profile = StudentProfile.objects.get(student=request.user)
    except StudentProfile.DoesNotExist:
        student_profile = None  # Set it to None or any default value based on your requirements

    context = {'user_profile': user_profile, 'student_profile': student_profile}
    return render(request, 'studentProfile.html', context)




from django.contrib import messages

@login_required
def student_edit_profile(request):
    user = request.user

    try:
        student_profile = StudentProfile.objects.get(student=user)
    except StudentProfile.DoesNotExist:
        student_profile = None

    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        user_profile = None

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        user_profile_form = EditUserProfileForm(request.POST, instance=user_profile)
        student_profile_form = StudentProfileForm(request.POST, request.FILES, instance=student_profile)

        if user_form.is_valid() and user_profile_form.is_valid() and student_profile_form.is_valid():
            user_instance = user_form.save()

            # Set the student field in StudentProfile
            student_profile_instance = student_profile_form.save(commit=False)
            student_profile_instance.student = user_instance
            student_profile_instance.save()

            user_profile_form.save()

            messages.success(request, 'Your profile was successfully updated.')  # Add a success message

            return redirect('student_profile')  # Assuming you have a URL named 'student_profile'
        else:
            messages.error(request, 'Please correct the errors below.')  # Add an error message
    else:
        user_form = UserUpdateForm(instance=user)
        user_profile_form = EditUserProfileForm(instance=user_profile)
        student_profile_form = StudentProfileForm(instance=student_profile)

    return render(request, 'student_edit_profile.html', {
        'user_form': user_form,
        'user_profile_form': user_profile_form,
        'student_profile_form': student_profile_form,
    })


from django.core.files.uploadedfile import SimpleUploadedFile

@login_required
def student_register_complaint(request):
    all_complaints = Complaint.objects.filter(student=request.user).order_by('-created_at')

    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.student = request.user

            # Check if a report file was provided in the form
            if 'report' in request.FILES:
                report_file = request.FILES['report']
                complaint.report = SimpleUploadedFile(report_file.name, report_file.read())

            complaint.save()
            messages.success(request, 'Complaint submitted successfully! We will review and update you soon.')
            return redirect('student_register_complaint')  # Redirect to the same page after successful form submission
    else:
        form = ComplaintForm()

    return render(request, 'student_register_complaints.html', {'form': form, 'all_complaints': all_complaints})


#Complaint History

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Complaint

@login_required
def student_complaint_history(request):
    all_complaints = Complaint.objects.filter(student=request.user).order_by('-created_at')
    return render(request, 'complaint_history.html', {'all_complaints': all_complaints})



@login_required
def staff_complaint_display(request):
    if request.method == 'POST':
        complaint_id = request.POST.get('complaint_id')
        complaint = get_object_or_404(Complaint, id=complaint_id)
        form = ComplaintUpdateForm(request.POST, instance=complaint)
        if form.is_valid():
            form.save()
            messages.success(request, 'Complaint status updated successfully!')
            return redirect('staff_complaint_display')  # Redirect to the same page after successful form submission

    all_complaints = Complaint.objects.select_related('student__userprofile').all().order_by('-created_at')

    complaint_update_form = ComplaintUpdateForm()

    return render(request, 'staff_complaint_display.html', {'all_complaints': all_complaints, 'complaint_update_form': complaint_update_form})



#Student List

from django.db.models import Q
import xlwt
from django.http import HttpResponse
@login_required
def student_list(request):
    query = request.GET.get('q')
    programme_query = request.GET.get('programme')

    # Exclude staff details using the is_staff field in UserProfile
    students = UserProfile.objects.exclude(is_staff=True)

    if query:
        students = students.filter(
            Q(user__username__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__email__icontains=query) |
            Q(programme__icontains=query)
        )

    if programme_query:
        students = students.filter(programme__icontains=programme_query)

    # Export to Excel functionality
    if 'export_excel' in request.GET:
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="student_details.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Student Details')

        # Style for header cells
        header_style = xlwt.XFStyle()
        header_font = xlwt.Font()
        header_font.bold = True
        header_font.height = 300  # Font size in 1/20th of a point
        header_style.font = header_font
        header_style.pattern = xlwt.Pattern()
        header_style.pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        header_style.pattern.pattern_fore_colour = xlwt.Style.colour_map['light_yellow']

        # Style for data cells
        data_style = xlwt.XFStyle()
        data_font = xlwt.Font()
        data_font.height = 240  # Font size in 1/20th of a point
        data_style.font = data_font

        # Headers
        headers = ['Register No.', 'Full Name', 'Programme', 'Email']
        for col_num, header in enumerate(headers):
            # Set width for each column
            ws.col(col_num).width = len(header) * 400
            ws.write(0, col_num, header, header_style)

        # Data
        for row_num, student in enumerate(students, start=1):
            ws.write(row_num, 0, student.user.username, data_style)
            ws.write(row_num, 1, student.user.get_full_name(), data_style)
            ws.write(row_num, 2, student.programme, data_style)
            ws.write(row_num, 3, student.user.email, data_style)

        wb.save(response)
        return response

    return render(request, 'student_list.html', {'students': students, 'query': query, 'programme_query': programme_query})



#Edit student list

@login_required
def edit_student(request, username):
    student = get_object_or_404(UserProfile, user__username=username)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=student.user)
        profile_form = EditUserProfileForm(request.POST, instance=student)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('student_list')

    else:
        user_form = UserUpdateForm(instance=student.user)
        profile_form = EditUserProfileForm(instance=student)

    return render(request, 'edit_student.html', {'user_form': user_form, 'profile_form': profile_form, 'student': student})


#Delete Student 

@login_required(login_url=None)
def delete_student(request, username):
    student = get_object_or_404(UserProfile, user__username=username)

    # Check if the request method is POST
    if request.method == 'POST':
        # Delete the student record
        student.user.delete()
        messages.success(request, f'Student {student.user.get_full_name()} deleted successfully.')
        return redirect('student_list')

    return redirect('student_list')

#staff Meeting

from .models import StaffMeeting
from .forms import StaffMeetingForm

@login_required
def add_staff_meeting(request):
    if request.method == 'POST':
        form = StaffMeetingForm(request.POST)
        if form.is_valid():
            staff_meeting = form.save(commit=False)
            staff_meeting.staff = request.user
            staff_meeting.save()
            return redirect('view_staff_meetings')
    else:
        form = StaffMeetingForm()

    return render(request, 'add_staff_meeting.html', {'form': form})


#view staff meetings

from django.utils import timezone
from django.shortcuts import render
from .models import StaffMeeting
from django.contrib.auth.decorators import login_required

@login_required
def view_staff_meetings(request):
    current_datetime = timezone.now()
    
    # Fetch all staff meetings without filtering by the current user
    staff_meetings = StaffMeeting.objects.all().order_by('-created_at')

    # Check and mark meetings as expired
    for meeting in staff_meetings:
        if meeting.meeting_datetime < current_datetime:
            meeting.is_expired = True
        else:
            meeting.is_expired = False

    return render(request, 'view_staff_meetings.html', {'staff_meetings': staff_meetings})




#Analytics 
from django.shortcuts import render
from django.db.models import Count

@login_required
def analytics(request):
    # Count complaints by status
    status_counts = Complaint.objects.values('status').annotate(count=Count('id'))

    # Count complaints by type
    type_counts = Complaint.objects.values('complaint_type').annotate(count=Count('id'))

    return render(request, 'analytics.html', {'status_counts': status_counts, 'type_counts': type_counts})


#Generate Report

from django.core.files.base import ContentFile


@login_required
def generate_report(request):
    if request.method == 'POST':
        complaint_id = request.POST.get('complaint_id')
        complaint = get_object_or_404(Complaint, id=complaint_id)

        # Generate PDF report
        template_path = 'generate_report_template.html'
        context = {'complaint': complaint}

        # Create a byte stream for the PDF content
        pdf_data = BytesIO()
        template = get_template(template_path)
        html = template.render(context)
        pisa.CreatePDF(html, dest=pdf_data)

        # Save the byte stream to the report field
        pdf_data.seek(0)
        complaint.report.save(f'{complaint.student.username}_complaint_report.pdf', ContentFile(pdf_data.read()), save=True)

        # Create a Django response object with appropriate PDF headers
        response = HttpResponse(pdf_data.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{complaint.student.username}_complaint_report.pdf"'

        return response

    return HttpResponse('Invalid request!', content_type='text/plain')
