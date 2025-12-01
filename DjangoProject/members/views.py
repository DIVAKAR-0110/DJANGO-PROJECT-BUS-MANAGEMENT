import os
import random, string, json
from datetime import timedelta, date
import qrcode
import re
from django.urls import reverse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.core.mail import EmailMessage
from reportlab.lib.units import mm
from django.http import FileResponse
import io
from django.http import HttpResponse
from django.shortcuts import render
from .models import Ticket
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.utils import timezone
from datetime import timedelta
from io import BytesIO
import base64
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.utils.dateparse import parse_date
from django.views import View
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.template.loader import get_template
from reportlab.lib.pagesizes import A4
from django.template.loader import get_template
from xhtml2pdf import pisa
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from PIL import Image as PILImage, ExifTags
from reportlab.platypus import Image
import qrcode
import io
from django.http import FileResponse
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.urls import reverse
from fpdf import FPDF
import random
import json
from django.utils.decorators import method_decorator

from .utils import send_receipt_email
import smtplib
from django.http import JsonResponse
from django.core.mail import send_mail
from decimal import Decimal, InvalidOperation
from django.core.files.storage import FileSystemStorage
from rest_framework.fields import empty
from unicodedata import category
from django.contrib.auth.models import User
from xhtml2pdf import pisa

from .models import *
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

def starting(request):
    return render(request, 'loading.html')

def terms_and_conditions(request):
    return render(request,'terms_and_conditions.html')

def mainpage(request):
    return render(request,'mainpage.html')

def adminstart(request):
    return render(request,'adminstart.html')

def about(request):
    return render(request,'about.html')

def contactus(request):
    return render(request,'contactus.html')

def college_register(request):
    if request.method == 'POST':
        name = request.POST.get('collegeName')
        code = request.POST.get('collegeCode')
        address = request.POST.get('location')
        admin_name = request.POST.get('adminName')
        admin_email = request.POST.get('adminEmail')
        admin_phone = request.POST.get('adminPhone')
        num_departments = request.POST.get('departments')
        working_hours = request.POST.get('workingHours')
        bus_certificate = request.FILES.get('busCert')

        username = request.POST.get('username')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')

        payment_methods = request.POST.getlist('paymentMethods')  # assuming multiple checkboxes
        custom_days_raw = request.POST.get('customDaysCount', '').strip()
        custom_days_count = int(custom_days_raw) if custom_days_raw.isdigit() else None

        if password != confirmpassword:
            messages.error(request, "Passwords do not match!")
            return render(request, 'clgapplication.html')

        hashed_password = make_password(password)

        college = College.objects.create(
            name=name,
            code=code,
            address=address,
            admin_name=admin_name,
            admin_email=admin_email,
            admin_phone=admin_phone,
            num_departments=num_departments,
            working_hours=working_hours,
            bus_certificate=bus_certificate,
            username=username,
            password=hashed_password,
            payment_methods=json.dumps(payment_methods),
            custom_days_count=custom_days_count,
        )

        messages.success(request, "College data saved successfully!")
        return redirect('register_success')

    return render(request, 'clgapplication.html')

@csrf_exempt  # only if CSRF token is not handled in JS
def contact_submit(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()

        # Validation
        if len(name) < 3 or not re.match(r'^[A-Za-z ]+$', name):
            return JsonResponse({'success': False, 'message': 'Please enter a valid name (letters only, min 3 characters).'})

        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            return JsonResponse({'success': False, 'message': 'Please enter a valid email address.'})

        if len(message) < 10:
            return JsonResponse({'success': False, 'message': 'Message must be at least 10 characters.'})

        # Save to DB
        ContactMessage.objects.create(name=name, email=email, message=message)
        return JsonResponse({'success': True, 'message': 'Your message has been sent successfully!'})

    return JsonResponse({'success': False, 'message': 'Invalid request!'})

def clgintropage(request):
    return render(request, 'tourmain.html')

def clgapplication(request):
    return render(request, 'clgapplication.html')

def college_requests(request):
    college = College.objects.all()
    return render(request, 'college_request.html', {'colleges': college})

def handle_college_action(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action:
            action_type, college_id = action.split('_')
            college = College.objects.get(id=college_id)

            if action_type == 'approve':
                # Check if already exists in ClgApproved
                if ClgApproved.objects.filter(
                        code=college.code,
                        admin_email=college.admin_email
                ).exists():
                    messages.warning(request, f"College '{college.name}' is already registered.")
                else:
                    ClgApproved.objects.create(
                        name=college.name,
                        code=college.code,
                        address=college.address,
                        admin_name=college.admin_name,
                        admin_email=college.admin_email,
                        admin_phone=college.admin_phone,
                        num_departments=college.num_departments,
                        working_hours=college.working_hours,
                        username=college.username + college.code,
                        password=college.password,
                        payment_methods=college.payment_methods,
                        custom_days_count=college.custom_days_count
                    )

                    send_mail(
                        subject='College Approval Notification',
                        message=(
                            f"Dear {college.admin_name},\n\n"
                            f"Congratulations! Your college '{college.name}' has been approved!\n"
                            f"Username: {college.username}{college.code}\n"
                            f"Password: {college.password}"
                        ),
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[college.admin_email],
                    )

                    college.delete()

            elif action_type == 'reject':
                reason = request.POST.get(f'reason_{college_id}')
                if not reason:
                    reason = 'No reason provided.'

                # Save to ClgRejected
                ClgRejected.objects.create(
                    name=college.name,
                    code=college.code,
                    address=college.address,
                    admin_name=college.admin_name,
                    admin_email=college.admin_email,
                    admin_phone=college.admin_phone,
                    num_departments=college.num_departments,
                    working_hours=college.working_hours,
                    reason=reason,
                    username=college.username,
                    password=college.password,
                    payment_methods=college.payment_methods,  # NEW
                    custom_days_count=college.custom_days_count  # NEW
                )

                # Send rejection email
                send_mail(
                    subject='College Rejection Notification',
                    message=(
                        f"Dear {college.admin_name},\n\n"
                        f"Unfortunately, your college '{college.name}' has been rejected.\n"
                        f"Reason: {reason}"
                    ),
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[college.admin_email],
                )
                college.delete()
    return redirect('college_requests')

def payment_error(request):
    return render(request, 'payment_error.html')


def register_success(request):
    return render(request,"registersuccess.html")

def admindashboard(request):
    college=ClgApproved.objects.all()
    student=ApprovedStudent.objects.all()
    college_count=college.count()
    print(college_count)
    student_count=student.count()
    print(student_count)
    busroutes_count=BusRoute.objects.all().count()

    print(busroutes_count)
    waiting_college_count=Student.objects.all().count()
    print(waiting_college_count)



    return render(request,'admindashboard.html',{'college':college,'student':student,
                                                 'college_count':college_count,'student_count':student_count,
                                                 'busroutes_count':busroutes_count,'waiting_college_count':waiting_college_count})


def collegeverify(request):
    if request.method == 'POST':
        college_name = request.POST.get('category')
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            college = ClgApproved.objects.get(name=college_name, username=username)
            student=Student.objects.all()
            # 👉 Direct comparison (for plain-text)
            if check_password(password,college.password):
                request.session['college_id'] = college.id
                goat = ClgApproved.objects.all()
                return render(request, 'collegemainpage.html', {
                    'college_id': college.id,
                    'college': college,
                    'goat': goat,
                    'student':student
                })
            else:
                messages.error(request, 'Invalid password.')
                return redirect('clgdashboard')

        except ClgApproved.DoesNotExist:
            messages.error(request, 'Invalid college name or username.')
            return redirect('clgdashboard')

    return redirect('clgdashboard')


def clgdashboard(request):
    colleges=ClgApproved.objects.all()

    return render(request,'clgdashboard.html',{'colleges':colleges})

def edit_college(request, id):
    goat = get_object_or_404(ClgApproved, id=id)
    req= id
    return render(request, 'edit_college.html', {'req': req, 'goat': goat })



def update_college(request, id):
    if request.method == 'POST':
        college = get_object_or_404(ClgApproved, id=id)
        college_id=id
        # Update basic fields
        college.name = request.POST.get('college_name')
        college.code = request.POST.get('college_code')
        college.address = request.POST.get('address')
        college.admin_name = request.POST.get('admin_name')
        college.admin_email = request.POST.get('admin_email')
        college.admin_phone = request.POST.get('admin_phone')
        college.working_hours = request.POST.get('working_hours')

        # Handle optional fields (file uploads)
        if 'image' in request.FILES and request.FILES['image']:
            college.image = request.FILES['image']

        if 'bus_certificate' in request.FILES and request.FILES['bus_certificate']:
            college.bus_certificate = request.FILES['bus_certificate']

        college.save()
        goat = ClgApproved.objects.all()
        # ✅ Use a valid redirect view name
        return render(request,'collegemainpage.html',{'college_id':college_id,'goat' : goat})  # Change to your desired view name

    # ⚠️ Optional: Handle wrong method types
    return redirect('edit_college', id=id)

def add_route(request, college_id):
    college = get_object_or_404(ClgApproved, id=college_id)

    if request.method == 'POST':
        route_name = request.POST.get('route_name')
        bus_number = request.POST.get('bus_number')
        number_of_seats = int(request.POST.get('number_of_seats'))
        driver_name = request.POST.get('driver_name')
        driver_contact_number = request.POST.get('driver_contact_number')

        morning_start = request.POST.get('morning_start')
        morning_end = request.POST.get('morning_end')
        morning_fare = float(request.POST.get('morning_fare') or 0)
        morning_time = request.POST.get('morning_time')

        BusRoute.objects.create(
            college=college,
            route_name=route_name,
            bus_number=bus_number,
            number_of_seats=number_of_seats,
            driver_name=driver_name,
            driver_contact_number=driver_contact_number,
            morning_start=morning_start,
            morning_end=morning_end,
            morning_fare=morning_fare,
            morning_time=morning_time
        )

        messages.success(request, "Morning bus route added successfully.")
        return redirect(reverse('successroute', args=[college_id, college.name]))

    return render(request, 'addroute.html', {'college': college, 'college_id': college.id})

def view_routes(request, college_id):
    college = get_object_or_404(ClgApproved, id=college_id)
    routes = BusRoute.objects.filter(college=college)
    return render(request, 'view_routes.html', {
        'college': college,
        'routes': routes,
        'college_id': college_id
    })


def successroute(request, college_id,college_name):
    college_id=college_id
    asdf=ClgApproved.objects.all()
    return render(request,"successroute.html",{'asdf':asdf,'college_id':college_id,'college_name':college_name})

def add_stop(request,route_id,route_name,college_id):
    route = get_object_or_404(BusRoute, id=route_id)
    route_name=route.route_name
    college_name = route.college.name.upper()
    return render(request,'addstops.html',{'route_id':route_id,'route_name':route_name,'college_id':college_id,'college_name':college_name })


def clean_price(value):
    return value.replace('₹', '').replace(',', '').strip()


def save_stop(request, route_id, route_name):
    route = get_object_or_404(BusRoute, id=route_id)
    college_id = route.college.id

    if request.method == 'POST':
        stop_ids = request.POST.getlist('stop_id[]')
        am_names = request.POST.getlist('am_stop_name[]')
        am_locations = request.POST.getlist('am_location[]')
        am_prices = request.POST.getlist('am_price[]')

        submitted_ids = set()

        for stop_id, name, location, price in zip(stop_ids, am_names, am_locations, am_prices):
            if name and location and price:
                try:
                    price_value = Decimal(clean_price(str(price)))
                except InvalidOperation:
                    messages.error(request, f"Invalid price: {price}")
                    return redirect(request.path)

                if stop_id:
                    try:
                        stop = Stop.objects.get(id=stop_id, route=route)
                        stop.name = name.strip()
                        stop.location = location.strip()
                        stop.price = price_value
                        stop.time_type = 'AM'
                        stop.save()
                        submitted_ids.add(int(stop_id))
                    except Stop.DoesNotExist:
                        # fallback to create new if not found
                        new_stop = Stop.objects.create(
                            route=route,
                            name=name.strip(),
                            location=location.strip(),
                            price=price_value,
                            time_type='AM'
                        )
                        submitted_ids.add(new_stop.id)
                else:
                    # New stop added
                    new_stop = Stop.objects.create(
                        route=route,
                        name=name.strip(),
                        location=location.strip(),
                        price=price_value,
                        time_type='AM'
                    )
                    submitted_ids.add(new_stop.id)

        # 🗑️ Delete stops that are no longer in the form
        Stop.objects.filter(route=route, time_type='AM').exclude(id__in=submitted_ids)

        messages.success(request, "Stops updated successfully.")
        return redirect('view_routes', college_id=college_id)

    return redirect('view_routes', college_id=college_id)


def view_stops(request, route_id, college_name):
    route = get_object_or_404(BusRoute, id=route_id)
    college_actual_name = route.college.name
    college_id = route.college.id

    # Compare names case-insensitively
    if college_actual_name.lower() == college_name.lower():
        stops = route.stops.all()
        context = {
            'route': route,
            'stops': stops,
            'college_name': college_actual_name,
            'college_id': college_id
        }
        return render(request, 'editstops.html', context)

    return redirect('view_routes', college_id=college_id)


def delete_route(request, route_id,college_id):
    route = get_object_or_404(BusRoute, id=route_id)
    college_id = route.college.id
    route.delete()
    return redirect('view_routes', college_id=college_id)

def edit_route(request, route_id, college_id):
    route = get_object_or_404(BusRoute, id=route_id)

    if request.method == 'POST':
        route.route_name = request.POST['route_name']
        route.bus_number = request.POST['bus_number']
        route.number_of_seats = request.POST['number_of_seats']
        route.driver_name = request.POST['driver_name']
        route.driver_contact_number = request.POST['driver_contact_number']
        route.morning_start = request.POST['morning_start']
        route.morning_end = request.POST['morning_end']
        route.morning_fare = request.POST['morning_fare']
        route.morning_time = request.POST['morning_time']

        route.save()
        messages.success(request, "Bus route edited successfully.")
        return redirect('view_routes', college_id=route.college.id)

    messages.error(request, "Bus route was not edited successfully.")
    return render(request, 'editroute.html', {'route': route, 'college_id': college_id})


def editroutes(request, route_id,college_id):
    route = get_object_or_404(BusRoute, id=route_id)
    return render(request, 'editroute.html', {'route': route,'college_id':college_id})



def forgot_passwords(request):
    colleges = ClgApproved.objects.all()
    return render(request, 'forgot_password.html', {'college': colleges})


def send_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        selected_college = request.POST.get('college')

        # Check if matching college and email exist
        college = ClgApproved.objects.filter(admin_email=email, name=selected_college).first()
        if not college:
            colleges = ClgApproved.objects.all()
            return render(request, 'forgot_password.html', {
                'college': colleges,
                'error': 'No matching college and email found.'
            })

        # Generate OTP
        otp = str(random.randint(100000, 999999))
        request.session['otp'] = otp
        request.session['email'] = email

        # Send OTP
        send_mail(
            subject="Your OTP for Password Reset",
            message=f"Your OTP is: {otp}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[college.admin_email],
            fail_silently=False,
        )

        colleges = ClgApproved.objects.all()
        return render(request, 'forgot_password.html', {
            'college': colleges,
            'step': 2,
            'email': email,
            'selected_college': selected_college,
            'college_username': college.username,
            'college_name':college.name
        })

    # Handle GET request gracefully
    colleges = ClgApproved.objects.all()
    return render(request, 'forgot_password.html', {
        'college': colleges
    })

def error(request):
    return render(request,'404page.html')

def verify_otp(request,college_username,college_name):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')

        if entered_otp == session_otp:
            request.session['otp_verified'] = True
            request.session['reset_password_email'] = request.session.get('email')

            colleges = ClgApproved.objects.all()
            return render(request, 'forgot_password.html', {
                'college': colleges,
                'college_username':college_username,
                'college_name':college_name,
                'step': 3
            })
        else:
            colleges = ClgApproved.objects.all()
            return render(request, 'forgot_password.html', {
                'college': colleges,
                'step': 2,
                'otp_error': 'Invalid OTP. Please try again.',
                'college_username': college_username,
                'college_name':college_name
            })

    return redirect('forgot_passwords')

def reset_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            colleges = ClgApproved.objects.all()
            return render(request, 'forgot_password.html', {
                'college': colleges,
                'step': 3,
                'error': 'Passwords do not match.'
            })

        email = request.session.get('reset_password_email')
        if not email:
            return redirect('forgot_passwords')

        try:
            college = ClgApproved.objects.filter(admin_email=email).first()

        except ClgApproved.DoesNotExist:
            colleges = ClgApproved.objects.all()
            return render(request, 'forgot_password.html', {
                'college': colleges,
                'step': 3,
                'error': 'College not found.'
            })
        print(college.code)
        # Update the college record
        college.username = username
        college.password = password
        college.save()

        # Clear session
        request.session.flush()

        return redirect('starting')  # or wherever your login page is


def studentdetails(request):
    college=ClgApproved.objects.all()
    return render(request,'studentdetails.html',{'college':college})

def student_choice(request):
    return render(request,'student_choice.html')

def students_login(request):
    return render(request,'students_login.html')

def student_register(request, college_id):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        student_id = request.POST.get('student_id')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        blood_group = request.POST.get('blood_group')
        student_photo = request.FILES.get('student_photo')
        course_name = request.POST.get('course_name')
        department = request.POST.get('department')
        year_semester = request.POST.get('year_semester')
        batch_year = request.POST.get('batch_year')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Check password match
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('studentdetails')

        # Check duplicate email
        if Student.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered!")
            return redirect('studentdetails')

        # Get the college object
        college = get_object_or_404(ClgApproved, id=college_id)

        # Hash password
        hashed_password = make_password(password)

        student = Student(
            full_name=full_name,
            student_id=student_id,
            dob=dob,
            gender=gender,
            blood_group=blood_group,
            student_photo=student_photo,
            course_name=course_name,
            department=department,
            year_semester=year_semester,
            batch_year=batch_year,
            phone_number=phone_number,
            email=email,
            password=hashed_password,
            college=college  # ✅ Assign FK object
        )
        student.save()
        messages.success(request, "Registration successful!")
        return render(request, 'student_success.html')

    # For GET requests
    return redirect('studentdetails')


def student_login_form(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        raw_password = request.POST.get('password')

        try:
            student = ApprovedStudent.objects.get(email=email)


            # Check hashed password
            if check_password(raw_password, student.password):
                request.session['student_id'] = student.id
                return redirect('student_dashboard', student_id=student.id)

            else:
                messages.error(request, 'Incorrect password.')
        except ApprovedStudent.DoesNotExist:
            messages.error(request, 'Student with this email does not exist.')

    return render(request, 'students_login.html')


def student_dashboard(request, student_id):
    student = get_object_or_404(ApprovedStudent, id=student_id)
    routes = BusRoute.objects.all()
    return render(request, 'student_dashboard.html', {
        'student_id': student.id,
        'student': student,
        'routes': routes
    })


def update_student_profile(request, student_id):
    student = get_object_or_404(ApprovedStudent, id=student_id)
    routes=BusRoute.objects.all()

    if request.method == 'POST':
        student.gender = request.POST.get('gender')
        student.phone_number = request.POST.get('phone_number')
        student.year_semester = request.POST.get('year_semester')
        student.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('student_dashboard', student_id=student.id)

    return render(request, 'student_dashboard.html', {
        'student_id': student.id,
        'student': student,
        'routes':routes
    })


def student_request(request, college_id):
    students = Student.objects.filter(college_id=college_id)
    college = ClgApproved.objects.all()
    return render(request, 'student_request.html', {
        'students': students,
        'college': college,
        'college_id': college_id
    })


def handle_student_request(request, student_id, college_id):
    student = get_object_or_404(Student, id=student_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            # Move to ApprovedStudent
            ApprovedStudent.objects.create(
                full_name=student.full_name,
                student_id=student.student_id,
                dob=student.dob,
                gender=student.gender,
                blood_group=student.blood_group,
                student_photo=student.student_photo,
                course_name=student.course_name,
                department=student.department,
                year_semester=student.year_semester,
                batch_year=student.batch_year,
                password=student.password,
                phone_number=student.phone_number,
                email=student.email,
                college=student.college.name,  # <-- Corrected here
                status='Approved'
            )

            send_mail(
                subject='Registration Approved',
                message=f"Dear {student.full_name},\n\nYour student registration at {student.college.name} has been approved. Your username is :{{  }}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[student.email],
                fail_silently=False,
            )

            student.delete()
            messages.success(request, f"{student.full_name} has been approved and notified by email.")
            return redirect('student_request', college_id=college_id)

        elif action == 'reject':
            reason = request.POST.get('rejection_reason', '')

            RejectedStudent.objects.create(
                full_name=student.full_name,
                student_id=student.student_id,
                dob=student.dob,
                gender=student.gender,
                blood_group=student.blood_group,
                student_photo=student.student_photo,
                course_name=student.course_name,
                department=student.department,
                year_semester=student.year_semester,
                batch_year=student.batch_year,
                password=student.password,
                phone_number=student.phone_number,
                email=student.email,
                college=student.college.name,  # <-- Corrected here
                status='Rejected',
                rejection_reason=reason
            )

            send_mail(
                subject='Registration Rejected',
                message=f"Dear {student.full_name},\n\nYour registration at {student.college.name} has been rejected.\n\nReason: {reason}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[student.email],
                fail_silently=False,
            )

            student.delete()
            messages.error(request, f"{student.full_name} has been rejected and notified by email.")
            return redirect('student_request', college_id=college_id)

    return redirect('student_request', college_id=college_id)


def student_routes(request, student_id):
    student = get_object_or_404(ApprovedStudent, student_id=student_id)
    college = ClgApproved.objects.filter(name=student.college).first()

    if college:
        bus_routes = BusRoute.objects.filter(college=college)
    else:
        bus_routes = []

    return render(request, 'routes_list.html', {
        'student': student,
        'studentsid':student.id,
        'student_id':student_id,
        'bus_routes': bus_routes
    })

def route_detail(request, route_id, student_id):
    student = get_object_or_404(ApprovedStudent, student_id=student_id)

    # Get route
    route = get_object_or_404(BusRoute, id=route_id)
    stops = route.stops.all()

    # Try resolving the college name to a ClgApproved instance
    college_instance = ClgApproved.objects.filter(name__iexact=student.college).first()

    # Match department in the resolved college
    department = Department.objects.filter(
        name__iexact=student.department,
        college=college_instance
    ).first()

    working_days = department.semester_working_days if department else 0

    context = {
        'route': route,
        'student': student,
        'stops': stops,
        'working_days': working_days
    }
    return render(request, 'route_detail.html', context)


def payment_page(request, route_id, stop_id, student_id):
    if request.method == 'POST':
        total_fare = request.POST.get('total_fare')
        return redirect(reverse('ticket_page', args=[route_id, stop_id, student_id]) + f'?total_fare={total_fare}')

    total_fare = request.GET.get('total_fare')
    return render(request, 'payment_module.html', {
        'total_fare': total_fare,
        'route_id': route_id,
        'stop_id': stop_id,
        'student_id': student_id
    })

def ticket_page(request, route_id, stop_id, student_id):
    student = get_object_or_404(ApprovedStudent, student_id=student_id)
    route = get_object_or_404(BusRoute, id=route_id)
    stop = get_object_or_404(Stop, id=stop_id)
    total_fare = request.GET.get('total_fare')

    start_date = timezone.now().date()
    end_date = start_date + timedelta(days=180)  # 6 months

    qr_text = f"Name: {student.full_name}\nID: {student.student_id}\nRoute: {route.route_name}\nFare: ₹{total_fare}\nStart: {start_date}\nEnd: {end_date}"
    qr = qrcode.make(qr_text)

    buffer = io.BytesIO()
    qr.save(buffer)
    qr_image = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'ticket_page.html', {
        'student': student,
        'route': route,
        'stop': stop,
        'total_fare': total_fare,
        'start_date': start_date,
        'end_date': end_date,
        'qr_image': qr_image,
        'qr_text': qr_text  # For confirm
    })

def confirm_payment(request, student_id, route_id, stop_id):
    if request.method == "POST":
        student = get_object_or_404(ApprovedStudent, id=student_id)
        route = get_object_or_404(BusRoute, id=route_id)
        stop = get_object_or_404(Stop, id=stop_id)
        total_fare = request.POST.get("total_fare")
        qr_data = request.POST.get("qr_data")

        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=180)

        ticket = Ticket.objects.create(
            student=student,
            route=route,
            stop=stop,
            total_fare=total_fare,
            start_date=start_date,
            end_date=end_date,
            qr_data=qr_data
        )

        return render(request, 'download_ticket.html', {"ticket": ticket})


def generate_ticket_pdf(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    p.setFont("Helvetica", 14)
    p.drawString(100, 800, "🚌 Bus Ticket")
    p.drawString(100, 780, f"Name: {ticket.student.full_name}")
    p.drawString(100, 760, f"Department: {ticket.student.department}")
    p.drawString(100, 740, f"Route: {ticket.route.route_name}")
    p.drawString(100, 720, f"Stop: {ticket.stop.name}")
    p.drawString(100, 700, f"Fare: ₹{ticket.total_fare}")
    p.drawString(100, 680, f"Valid: {ticket.start_date} to {ticket.end_date}")

    qr = qrcode.make(ticket.qr_data)
    qr_buffer = io.BytesIO()
    qr.save(qr_buffer)
    qr_buffer.seek(0)

    p.drawInlineImage(qr_buffer, 100, 500, width=100, height=100)

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='ticket.pdf')


def scan_qr_data(request):
    if request.method == 'POST':
        qr_text = request.POST.get('qr_data')
        try:
            ticket = Ticket.objects.get(qr_data=qr_text)
            return JsonResponse({
                "status": "valid",
                "student": ticket.student.full_name,
                "department": ticket.student.department,
                "route": ticket.route.route_name,
                "stop": ticket.stop.name,
                "valid_till": str(ticket.end_date)
            })
        except Ticket.DoesNotExist:
            return JsonResponse({"status": "invalid"})


@csrf_exempt
def process_payment(request):
    try:
        if request.method == "POST":
            method = request.POST.get("payment_method")
            student_id = request.POST.get("student_id")
            route_id = request.POST.get("route_id")
            stop_id = request.POST.get("stop_id")
            total_fare = request.POST.get("total_fare")

            if not all([method, student_id, route_id, total_fare, stop_id]):
                messages.error(request, "Missing required fields.")
                return redirect('payment_error')

            # ✅ Fetch student, route, stop
            student = get_object_or_404(ApprovedStudent, student_id=student_id)
            route = get_object_or_404(BusRoute, id=route_id)
            stop = get_object_or_404(Stop, id=stop_id)

            # ✅ Check seat availability
            if route.filled_seats >= route.number_of_seats:
                messages.error(request, "No available seats on this bus route.")
                return redirect('route_detail', route_id=route.id, student_id=student.student_id)

            # ✅ Create Payment object
            payment = Payment(
                method=method,
                student=student,
                ticket=None,  # Will generate ticket after
                total_fare=total_fare
            )

            # Optional fields based on payment method
            if method == 'card':
                payment.card_name = request.POST.get("card_name")
                payment.card_number = request.POST.get("card_number")
                payment.expiry = request.POST.get("expiry")
            elif method == 'upi':
                payment.upi_id = request.POST.get("upi_id")
            elif method == 'netbanking':
                payment.bank = request.POST.get("bank")
            elif method == 'wallet':
                payment.wallet_id = request.POST.get("wallet_id")
            elif method == 'prepaid':
                payment.prepaid_card_number = request.POST.get("prepaid_card_number")
                payment.prepaid_pin = request.POST.get("prepaid_pin")

            payment.save()

            # ✅ Generate Ticket for this payment
            from datetime import datetime, timedelta
            ticket = Ticket.objects.create(
                student=student,
                route=route,
                stop=stop,
                total_fare=total_fare,
                start_date=datetime.today(),
                end_date=datetime.today() + timedelta(days=30),  # Example: 1 month validity
                qr_data=f"{student.student_id}_{route.id}_{stop.id}_{datetime.now().timestamp()}"
            )
            payment.ticket = ticket
            payment.save()

            # ✅ Update route seats
            route.filled_seats += 1
            route.available_seats = max(route.number_of_seats - route.filled_seats, 0)
            route.save()

            # ✅ Optional: send receipt email
            send_receipt_email(payment)
            redirect_url = reverse('receipt_view', kwargs={'payment_id': payment.id})
            return JsonResponse(
                {"status": "success", "message": f"Payment of ₹{total_fare} successful!", "redirect_url": redirect_url})
        else:
            messages.error(request, "Invalid request method.")
            return redirect('payment_error')

    except Exception as e:
        print("Payment processing error:", str(e))
        messages.error(request, "Something went wrong while processing your payment.")
        return redirect('payment_error')


# members/views.py
def receipt_view(request, payment_id):
    payment = Payment.objects.get(id=payment_id)
    return render(request, 'receipt.html', {'payment': payment})


def approved_colleges(request):
    query = request.GET.get('q', '')
    if query:
        colleges = ClgApproved.objects.filter(name__icontains=query) | ClgApproved.objects.filter(code__icontains=query)
    else:
        colleges = ClgApproved.objects.all()
    return render(request, 'approved_colleges.html', {'colleges': colleges, 'query': query})

def rejected_colleges(request):
    query = request.GET.get('q', '')
    if query:
        colleges = ClgRejected.objects.filter(name__icontains=query) | ClgRejected.objects.filter(code__icontains=query)
    else:
        colleges = ClgRejected.objects.all()
    return render(request, 'rejected_colleges.html', {'colleges': colleges, 'query': query})

















def view_approved_students(request, college_id):
    college = get_object_or_404(ClgApproved, id=college_id)
    students = ApprovedStudent.objects.filter(college=college.name)  # college name is stored as string

    # Optional: get distinct departments for the dropdown filter in HTML
    departments = ApprovedStudent.objects.filter(college=college.name).values_list('department', flat=True).distinct()

    return render(request, 'approved_students.html', {
        'students': students,
        'college': college,
        'departments': departments,
    })


class ForgotPasswordView(View):
    def get(self, request):
        return render(request, 'student_forgotpassword.html')


def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))


def verify_email_college(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')

    data = json.loads(request.body)
    email = data.get('email', '').strip().lower()
    college = data.get('college', '').strip()

    if not email or not college:
        return JsonResponse({'success': False, 'message': 'Email and college required'})

    try:
        student = ApprovedStudent.objects.get(email__iexact=email, college__iexact=college)
    except ApprovedStudent.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'No matching student found'})

    otp = generate_otp()
    request.session['otp'] = otp
    request.session['otp_time'] = timezone.now().isoformat()
    request.session['email'] = email

    subject = "Your OTP for Password Reset"
    message = f"Hi {student.full_name},\nYour OTP is: {otp}\nThis OTP expires in 2 minutes."

    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        return JsonResponse({'success': True, 'message': 'OTP sent'})
    except Exception:
        return JsonResponse({'success': False, 'message': 'Failed to send OTP'})


def verifying_otp(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')

    data = json.loads(request.body)
    email = data.get('email', '').strip().lower()
    otp = data.get('otp', '').strip()

    if request.session.get('email') != email or request.session.get('otp') != otp:
        return JsonResponse({'success': False, 'message': 'OTP mismatch or email mismatch'})

    time_sent = timezone.datetime.fromisoformat(request.session.get('otp_time'))
    if (timezone.now() - time_sent).total_seconds() > 120:
        return JsonResponse({'success': False, 'message': 'OTP expired'})

    request.session['otp_verified'] = True
    return JsonResponse({'success': True, 'message': 'OTP verified'})


def resetting_password(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')

    if not request.session.get('otp_verified'):
        return JsonResponse({'success': False, 'message': 'OTP not verified'})

    data = json.loads(request.body)
    new_password = data.get('password')
    email = request.session.get('email')

    if not new_password or len(new_password) < 6:
        return JsonResponse({'success': False, 'message': 'Password must be at least 6 characters'})

    try:
        student = ApprovedStudent.objects.get(email=email)
        student.password = make_password(new_password)
        student.save()
        request.session.flush()
        return JsonResponse({'success': True, 'message': 'Password reset successfully'})
    except ApprovedStudent.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Student not found'})



def departmentmainpage(request,college_id):
    colleges=ClgApproved.objects.all()
    return render(request,'department.html',{'colleges':colleges,'college_id':college_id})



def calculate_working_days(start_date, end_date):
    count = 0
    current = start_date
    while current <= end_date:
        if current.weekday() != 6:  # Skip Sundays
            count += 1
        current += timedelta(days=1)
    return count



# ----------------------- DEPARTMENT VIEWS -----------------------
def add_department(request, college_id):
    college = get_object_or_404(ClgApproved, id=college_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        semester_count = request.POST.get('semester_count')
        number_of_students = request.POST.get('number_of_student_in_this_department')
        department_head = request.POST.get('department_head')
        department_email = request.POST.get('department_email')
        contact_number = request.POST.get('contact_number')
        established_year = request.POST.get('established_year')
        description = request.POST.get('description')
        notes = request.POST.get('notes')
        department_code = request.POST.get('department_code', 'Not updated !')
        logo = request.FILES.get('department_logo')

        # Convert dates to Python date objects
        start_date_obj = date.fromisoformat(start_date)
        end_date_obj = date.fromisoformat(end_date)

        # Calculate working days
        working_days = calculate_working_days(start_date_obj, end_date_obj)

        # Save department
        Department.objects.create(
            college=college,
            name=name,
            start_date=start_date_obj,
            end_date=end_date_obj,
            semester_count=semester_count,
            semester_working_days=working_days,
            number_of_student_in_this_department=number_of_students,
            department_head=department_head,
            department_email=department_email,
            department_code=department_code,
            contact_number=contact_number,
            department_logo=logo,
            established_year=established_year,
            description=description,
            notes=notes
        )

        messages.success(request, "Department created successfully!")
        return redirect('view_departments', college_id=college_id)

    return render(request, 'add_department.html', {'college': college,'college_id':college_id})

def view_departments(request, college_id):
    search_query = request.GET.get('search', '')
    departments = Department.objects.filter(college_id=college_id)

    if search_query:
        departments = departments.filter(
            Q(name__icontains=search_query) |
            Q(department_code__icontains=search_query) |
            Q(courses__course_name__icontains=search_query)
        ).distinct()

    paginator = Paginator(departments, 3)  # 3 departments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'view_departments.html', {
        'departments': page_obj
    })

def edit_department(request, id):
    department = get_object_or_404(Department, id=id)

    if request.method == 'POST':
        department.name = request.POST.get('name')
        department.start_date = date.fromisoformat(request.POST.get('start_date'))
        department.end_date = date.fromisoformat(request.POST.get('end_date'))
        department.semester_count = request.POST.get('semester_count')
        department.number_of_student_in_this_department = request.POST.get('number_of_student_in_this_department')
        department.department_head = request.POST.get('department_head')
        department.department_email = request.POST.get('department_email')
        department.contact_number = request.POST.get('contact_number')
        department.established_year = request.POST.get('established_year')
        department.description = request.POST.get('description')
        department.notes = request.POST.get('notes')
        department.department_code = request.POST.get('department_code', 'Not updated !')

        if request.FILES.get('department_logo'):
            department.department_logo = request.FILES.get('department_logo')

        # Recalculate working days
        department.semester_working_days = calculate_working_days(department.start_date, department.end_date)

        department.save()
        messages.success(request, "Department updated successfully!")
        return redirect('view_departments', college_id=department.college.id)

    return render(request, 'edit_department.html', {'department': department})


def delete_department(request, id):
    department = get_object_or_404(Department, id=id)

    if request.method == 'POST':  # Only allow deletion via POST
        college_id = department.college.id
        department.delete()
        messages.success(request, "Department deleted successfully!")
        return redirect('view_departments', college_id=college_id)

    messages.warning(request, "Invalid request method for deletion.")
    return redirect('view_departments', college_id=department.college.id)



def add_course(request, department_id):
    department = get_object_or_404(Department, id=department_id)

    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        course_code = request.POST.get('course_code')
        duration = request.POST.get('duration')
        level = request.POST.get('level')
        course_head = request.POST.get('course_head')
        head_email = request.POST.get('head_email')
        contact_number = request.POST.get('contact_number')
        syllabus_pdf = request.FILES.get('syllabus_pdf')

        Course.objects.create(
            department=department,
            course_name=course_name,
            course_code=course_code,
            duration=duration,
            level=level,
            course_head=course_head,
            head_email=head_email,
            contact_number=contact_number,
            syllabus_pdf=syllabus_pdf
        )

        messages.success(request, 'Course added successfully.')
        return redirect('view_departments', college_id=department.college.id)

    return render(request, 'add_course.html', {'department': department})


def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        course.course_name = request.POST.get('course_name')
        course.course_code = request.POST.get('course_code')
        course.duration = request.POST.get('duration')
        course.level = request.POST.get('level')
        course.course_head = request.POST.get('course_head')
        course.head_email = request.POST.get('head_email')
        course.contact_number = request.POST.get('contact_number')

        if 'syllabus_pdf' in request.FILES:
            course.syllabus_pdf = request.FILES['syllabus_pdf']

        course.save()
        messages.success(request, "Course updated successfully!")
        return redirect('view_departments', course.department.college.id)

    return render(request, 'edit_course.html', {'course': course})


def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    college_id = course.department.college.id  # get before deleting
    course.delete()
    messages.success(request, "Course deleted successfully.")
    return redirect('view_departments', college_id)