from django.db import models
from django.utils import timezone
from enum import unique

from django.contrib.auth.hashers import make_password
from cryptography.fernet import Fernet
from django.conf import settings
import json
from django.db import models



class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    branch = models.CharField(max_length=50,default='not given')
    blood_group = models.CharField(max_length=50,default='not given')
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    dob = models.DateField()
    profile_image = models.ImageField(upload_to='profile_pics/', default='profile_pics/img_1.png',blank=True)

    def __str__(self):
        return self.username


class College(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100, unique=True)
    address = models.TextField()
    admin_name = models.CharField(max_length=100)
    admin_email = models.EmailField()
    admin_phone = models.CharField(max_length=15)
    num_departments = models.PositiveIntegerField()
    working_hours = models.CharField(max_length=100)
    bus_certificate = models.FileField(upload_to='bus_certificates/')

    username = models.CharField(max_length=100, unique=True,default='username')
    password = models.CharField(max_length=128,default='password')

    payment_methods = models.TextField(default='[]')  # Will store JSON list like ["daily", "monthly"]
    custom_days_count = models.PositiveIntegerField(null=True, blank=True)  # Optional if "custom_days" selected

    def save(self, *args, **kwargs):
        # Hash password if not already hashed
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def set_payment_methods(self, methods_list):
        """Use this to set payment methods from Python list"""
        self.payment_methods = json.dumps(methods_list)

    def get_payment_methods(self):
        """Use this to get payment methods as Python list"""
        try:
            return json.loads(self.payment_methods)
        except json.JSONDecodeError:
            return []

    def __str__(self):
        return f"{self.name} ({self.code})"



class ClgApproved(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100, unique=True)
    address = models.TextField()
    admin_name = models.CharField(max_length=100)
    admin_email = models.EmailField(unique=True)
    admin_phone = models.CharField(max_length=15)
    num_departments = models.PositiveIntegerField()
    working_hours = models.CharField(max_length=100)
    image = models.ImageField(upload_to='college_images/', blank=True, null=True)
    bus_certificate = models.FileField(upload_to='bus_certificates/', null=True, blank=True)

    username = models.CharField(max_length=100, unique=True,default='username')
    password = models.CharField(max_length=128,default='password')

    payment_methods = models.TextField(default='[]')  # Will store JSON list like ["daily", "monthly"]
    custom_days_count = models.PositiveIntegerField(null=True, blank=True)  # Optional if "custom_days" selected

    def save(self, *args, **kwargs):
        # Hash password if not already hashed
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def set_payment_methods(self, methods_list):
        """Use this to set payment methods from Python list"""
        self.payment_methods = json.dumps(methods_list)

    def get_payment_methods(self):
        """Use this to get payment methods as Python list"""
        try:
            return json.loads(self.payment_methods)
        except json.JSONDecodeError:
            return []

    def __str__(self):
        return f"{self.name} ({self.code})"


class ClgRejected(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100, unique=True)
    address = models.TextField()
    admin_name = models.CharField(max_length=100)
    admin_email = models.EmailField()
    admin_phone = models.CharField(max_length=15)
    num_departments = models.PositiveIntegerField()
    working_hours = models.CharField(max_length=100)
    reason = models.TextField()

    username = models.CharField(max_length=100, unique=True,default='username')
    password = models.CharField(max_length=128,default='password')

    payment_methods = models.TextField(default='[]')  # Will store JSON list like ["daily", "monthly"]
    custom_days_count = models.PositiveIntegerField(null=True, blank=True)  # Optional if "custom_days" selected

    def save(self, *args, **kwargs):
        # Hash password if not already hashed
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def set_payment_methods(self, methods_list):
        """Use this to set payment methods from Python list"""
        self.payment_methods = json.dumps(methods_list)

    def get_payment_methods(self):
        """Use this to get payment methods as Python list"""
        try:
            return json.loads(self.payment_methods)
        except json.JSONDecodeError:
            return []

    def __str__(self):
        return f"{self.name} ({self.code})"

class BusRoute(models.Model):
    college = models.ForeignKey(ClgApproved, on_delete=models.CASCADE, related_name='bus_routes')
    route_name = models.CharField(max_length=200)
    bus_number = models.CharField(max_length=50)
    number_of_seats = models.PositiveIntegerField()
    available_seats=models.PositiveIntegerField(default=0)
    filled_seats=models.PositiveIntegerField(default=0)
    driver_name = models.CharField(max_length=100)
    driver_contact_number = models.CharField(max_length=15)

    # Morning Route
    morning_start = models.CharField(max_length=100, null=True, blank=True)
    morning_end = models.CharField(max_length=255)
    morning_fare = models.DecimalField(max_digits=6, decimal_places=2)
    morning_time = models.TimeField()

    def __str__(self):
        return f"{self.route_name} - {self.bus_number} ({self.college.code})"



class Stop(models.Model):
    TIME_CHOICES = [
        ('AM', 'Morning'),
        ('PM', 'Evening')
    ]
    route = models.ForeignKey(BusRoute, on_delete=models.CASCADE, related_name='stops')
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    time_type = models.CharField(max_length=2, choices=TIME_CHOICES,default='AM')

    def __str__(self):
        return f"{self.name} - {self.time_type}"

class Department(models.Model):
    college = models.ForeignKey(ClgApproved, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    semester_count = models.IntegerField()
    semester_working_days = models.IntegerField(default=0)
    number_of_student_in_this_department = models.IntegerField()
    department_head = models.CharField(max_length=255)
    department_email = models.EmailField(blank=True, null=True)
    department_code=models.CharField(default='Not updated !')
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    department_logo = models.ImageField(upload_to='department_logos/', blank=True, null=True)
    established_year = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField(blank=True)
    notes=models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.college.name}"

class Course(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    course_name = models.CharField(max_length=255)
    course_code = models.CharField(max_length=50)
    duration = models.CharField(max_length=50)
    level = models.CharField(max_length=20, choices=[
        ('UG', 'Undergraduate'),
        ('PG', 'Postgraduate'),
        ('DIPLOMA', 'Diploma'),
        ('PhD', 'Doctorate')
    ])
    course_head = models.CharField(max_length=255, null=True)
    head_email = models.EmailField(blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    syllabus_pdf = models.FileField(upload_to='syllabus/', null=True, blank=True)
    def __str__(self):
        return f"{self.course_name} ({self.course_code})"







class Student(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')
    ]

    full_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20, unique=True)
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    student_photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    course_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    year_semester = models.CharField(max_length=50)
    batch_year = models.CharField(max_length=20)
    password = models.CharField(max_length=100, default='default_password')
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    college = models.ForeignKey(ClgApproved, on_delete=models.CASCADE, null=True,blank=True,related_name='register_students')
    status = models.CharField(
        max_length=10,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending'
    )

    def __str__(self):
        return self.full_name


class ApprovedStudent(models.Model):
    full_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20)
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    blood_group = models.CharField(max_length=3)
    student_photo = models.ImageField(upload_to='approved_students/', blank=True, null=True)
    course_name = models.CharField(max_length=100)
    assigned_route = models.ForeignKey(BusRoute, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_stop = models.ForeignKey(Stop, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.CharField(max_length=100)
    year_semester = models.CharField(max_length=50)
    batch_year = models.CharField(max_length=20)
    password = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    college = models.CharField(max_length=100,null=True)
    status = models.CharField(max_length=10, default='Denied')

class RejectedStudent(models.Model):
    full_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20, unique=True)
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    blood_group = models.CharField(max_length=3)
    student_photo = models.ImageField(upload_to='rejected_students/', blank=True, null=True)
    course_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    year_semester = models.CharField(max_length=50)
    batch_year = models.CharField(max_length=20)
    password = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    college = models.CharField(max_length=100,null=True)
    status = models.CharField(max_length=10, default='Rejected')
    rejection_reason = models.TextField()


class Ticket(models.Model):
    student = models.ForeignKey(ApprovedStudent, on_delete=models.CASCADE)
    route = models.ForeignKey(BusRoute, on_delete=models.CASCADE)
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    total_fare = models.DecimalField(max_digits=8, decimal_places=2)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    qr_data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Payment(models.Model):
    PAYMENT_METHODS = [
        ('card', 'Card'),
        ('netbanking', 'NetBanking'),
        ('upi', 'UPI'),
        ('wallet', 'Digital Wallet'),
        ('prepaid', 'Prepaid Card'),
    ]

    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    card_name = models.CharField(max_length=100, blank=True, null=True)
    card_number = models.CharField(max_length=16, blank=True, null=True)
    expiry = models.CharField(max_length=10, blank=True, null=True)
    upi_id = models.CharField(max_length=100, blank=True, null=True)
    bank = models.CharField(max_length=100, blank=True, null=True)
    wallet_id = models.CharField(max_length=100, blank=True, null=True)
    prepaid_card_number = models.CharField(max_length=16, blank=True, null=True)
    prepaid_pin = models.CharField(max_length=10, blank=True, null=True)

    student = models.ForeignKey(ApprovedStudent, on_delete=models.CASCADE, null=True, blank=True)
    ticket = models.OneToOneField(Ticket, on_delete=models.SET_NULL, null=True, blank=True)
    total_fare = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.full_name if self.student else 'Unknown'} - {self.method.title()} - ₹{self.total_fare}"