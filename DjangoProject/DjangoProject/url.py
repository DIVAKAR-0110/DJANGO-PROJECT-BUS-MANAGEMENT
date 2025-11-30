from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.static import static
from members import views


urlpatterns = [
    path('admin/', admin.site.urls),

    path('adminstart/',views.adminstart,name='adminstart'),
    path('admindashboard',views.admindashboard,name='admindashboard'),


    #path('asd/', views.signin, name='signin'),
    #path('starting/<str:email>/', views.starting, name='starting'),
    #path('home/<str:email>/',views.home,name='home'),
    #path('renew/',views.renew,name='renew'),
    #path('register/',views.register,name='register'),
    #path('help_support/',views.help_support,name='help_support'),
    #path('cancel/',views.cancel,name='cancel'),
    #path('status/',views.status,name='status'),
    # clgintropage

    path('', views.starting, name='starting'),
    path('mainpage/',views.mainpage,name='mainpage'),
    path('about/',views.about,name='about'),
    path('contactus/',views.contactus,name='contactus'),
    path('contact_submit/',views.contact_submit,name='contact_submit'),
    path('college_register/', views.college_register, name='college_register'),
    path('terms_and_conditions/',views.terms_and_conditions,name='terms_and_conditions'),
    path('clgapplication/', views.clgapplication, name='clgapplication'),
    path('college_requests/', views.college_requests, name='college_requests'),
    path('handle_college_action/', views.handle_college_action, name='handle_college_action'),
    path('registersuccess/',views.register_success,name='register_success'),
    path('forgot_passwords/', views.forgot_passwords, name='forgot_passwords'),
    path('send_otp/', views.send_otp, name='send_otp'),
    path('verify_otp/<str:college_username>/<str:college_name>/', views.verify_otp, name='verify_otp'),
    path('reset_password/', views.reset_password, name='reset_password'),


    path('clgdashboard/',views.clgdashboard,name='clgdashboard'),
    path('collegeverify/', views.collegeverify, name='collegeverify'),
    path('edit_college/<int:id>/', views.edit_college, name='edit_college'),
    path('update_college/<int:id>/', views.update_college, name='update_college'),
    path('addroute/<int:college_id>/', views.add_route, name='addroute'),
    path('successroute/<int:college_id>/<str:college_name>/',views.successroute,name='successroute'),
    path('view_routes/<int:college_id>/', views.view_routes, name='view_routes'),
    path('edit_route/<int:route_id>/<int:college_id>/',views.edit_route,name='edit_route'),
    path('editroutes/<int:route_id>/<int:college_id>/', views.editroutes, name='editroutes'),
    path('deleteroutes/<int:route_id>/<int:college_id>/',views.delete_route,name='deleteroutes'),
    path('view_stops/<int:route_id>/<str:college_name>/',views.view_stops,name='view_stops'),
    path('add_stop/<int:route_id>/<str:route_name>/<int:college_id>/',views.add_stop,name='add_stop'),
    path('save_stop/<int:route_id>/<str:route_name>/',views.save_stop,name='save_stop'),


    path('student_request/<int:college_id>/', views.student_request, name='student_request'),
    path('handle_student_request/<int:student_id>/<int:college_id>/', views.handle_student_request, name='handle_student_request'),



    path('studentdetails/',views.studentdetails,name='studentdetails'),
    path('student_choice/',views.student_choice,name='student_choice'),
    path('students_login/',views.students_login,name='students_login'),
    path('student_login_form',views.student_login_form,name="student_login_form"),
    path('student_dashboard/<int:student_id>/', views.student_dashboard, name='student_dashboard'),



    path('studentregister/<int:college_id>/', views.student_register, name='student_register'),
    path('update_student_profile/<int:student_id>/', views.update_student_profile, name='update_student_profile'),

    path('view_approved_students/<int:college_id>/', views.view_approved_students, name='view_approved_students'),




    path('forgot_password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('forgot-password/verify/', views.verify_email_college, name='forgot_password_verify'),
    path('forgot-password/verify-otp/', views.verifying_otp, name='forgot_password_verify_otp'),
    path('forgot-password/reset/', views.resetting_password, name='forgot_password_reset'),


    path('student_routes/<str:student_id>/', views.student_routes, name='student_routes'),
    path('route_detail/<int:route_id>/<str:student_id>/', views.route_detail, name='route_detail'),
    path('payment_page/<int:route_id>/<int:stop_id>/<str:student_id>/', views.payment_page, name='payment_page'),
    path('ticket_page/<int:route_id>/<int:stop_id>/<str:student_id>/', views.ticket_page, name='ticket_page'),
    path('confirm_payment/<int:student_id>/<int:route_id>/<int:stop_id>/', views.confirm_payment, name='confirm_payment'),
    path('generate_ticket_pdf/<int:ticket_id>/', views.generate_ticket_pdf, name='generate_ticket_pdf'),
    path('verify_qr/', views.scan_qr_data, name='scan_qr_data'),


    #path('payment_form_page/<int:route_id>/<int:stop_id>/', views.payment_form_page, name='payment_form_page'),
    path('process_payment/', views.process_payment, name='process_payment'),
    path('receipt/<int:payment_id>/', views.receipt_view, name='receipt_view'),
    path('payment_error/', views.payment_error, name='payment_error'),


    path('departmentmainpage/<int:college_id>/',views.departmentmainpage,name='departmentmainpage'),
    path('add_department/<int:college_id>/',views.add_department,name='add_department'),
    path('view_departments/<int:college_id>/',views.view_departments,name='view_departments'),
    path('edit_department/<int:id>/', views.edit_department, name='edit_department'),
    path('delete_department/<int:id>/', views.delete_department, name='delete_department'),

    path('add_course/<int:department_id>/', views.add_course, name='add_course'),
    path('edit_course/<int:course_id>/', views.edit_course, name='edit_course'),
    path('delete_course/<int:course_id>/', views.delete_course, name='delete_course'),

    path('approved_colleges',views.approved_colleges,name='approved_colleges'),
    path('rejected_colleges',views.rejected_colleges,name='rejected_colleges'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


