# members/utils.py
from django.core.mail import send_mail
from django.conf import settings

def send_receipt_email(payment):
    """
    Sends receipt email to the student after successful payment.
    """
    try:
        subject = f"Bus Ticket Receipt - {payment.student.full_name}"
        message = f"""
        Hi {payment.student.full_name},

        Your payment of ₹{payment.total_fare} for route {payment.ticket.route.route_name} has been successfully processed.

        Ticket ID: {payment.ticket.id}
        Stop: {payment.ticket.stop.name}
        Start Date: {payment.ticket.start_date}
        End Date: {payment.ticket.end_date}

        Thank you for using College Bus Management System!
        """
        recipient_list = [payment.student.email]
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
    except Exception as e:
        print("Failed to send receipt email:", e)
