from django.contrib import admin

from .models import *

admin.site.register(User)
admin.site.register(College)
admin.site.register(ClgApproved)
admin.site.register(ClgRejected)
admin.site.register(BusRoute)
admin.site.register(Stop)
admin.site.register(Student)
admin.site.register(ApprovedStudent)
admin.site.register(RejectedStudent)
admin.site.register(Payment)
admin.site.register(Department)
admin.site.register(Course)
admin.site.register(Ticket)
