from django.contrib import admin

# Register your models here.
from .models import tutorMeUser,Course,Schedule, ScheduleStudent, Appointment, ChatMessage, Notification
admin.site.register(tutorMeUser)
admin.site.register(ChatMessage)


class MyModelAdmin(admin.ModelAdmin):
    list_display =["Subject","course_name","course_number"]
admin.site.register(Course,MyModelAdmin)

class MySchedule(admin.ModelAdmin):
    list_display =["tutor","class_name"]
admin.site.register(Schedule,MySchedule)

class studentSchedule(admin.ModelAdmin):
    list_display =["student", "tutor","class_name"]
admin.site.register(ScheduleStudent,studentSchedule)


class AppointmentAdmin(admin.ModelAdmin):
    list_display =["student", "tutor","class_name"]
admin.site.register(Appointment,AppointmentAdmin)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('state', 'tutor', 'student', 'class_name', 'time')
admin.site.register(Notification, NotificationAdmin)
