from django.urls import path
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('sendback',views.send_to_home,name="returnHome"),
    path('accounts/', include('allauth.urls')),
    path('logout', LogoutView.as_view()),
    path('reportBug',views.bug_report_view, name="bugReport"),
    path('tutorMe/logout', LogoutView.as_view()),
    path('tutorCheck/', views.tutor_check),

    path('student', views.StudentView, name='student_default'),

    path('tutor', views.TutorView, name="tutor"),

    path('delete/<str:Class>/', views.deleteClass, name='delete_item'),
    path('add/<str:mnemonic>/<str:name>/<str:number>/', views.addClass, name='add_item'),
    path('student/classes', views.Student_Classes_View),
    # path('tutor/classes', views.Tutor_Classes_View),

    path('student/classes/list', views.Student_Classes_List_View, name='student_classes_list_view'),
    path('tutor/classes/list', views.Tutor_Classes_List_View, name='tutor_classes_list_view'),
    path('tutor/classes', views.searchView),
    path('check/<str:mnemonic>/<str:name>/<str:number>/', views.Student_Classes_List_View, name='check'),
    path('schedule/<str:tutor>/<str:name>/<str:mnemonic>', views.StudentMakeSchedule, name='student_make_schedule'),

    path('tutor/classes/list/<str:name>', views.schedule_view, name='schedule'),
    path('tutor/classes/list/edit/<str:name>', views.EditClass, name='edit'),
    path('tutor/classes/<str:class_name>/times', views.calendar_times, name='calendar_times'),

    path('schedule/<str:tutor>/<str:name>/<str:mnemonic>/times', views.calendarStudent, name='calendar_student'),

    path('tutor/requests', views.tutorRequests, name='tutor_requests'),
    path('student/requests', views.studentRequests, name='student_requests'),

    path('delete/<str:class_name>/<str:tutor>/<str:student>/', views.deleteRequest, name='delete_request'),
    path('accept/<str:class_name>/<str:tutor>/<str:student>/', views.accepted, name='accepted'),
    path('tutor/appointments', views.allAppointmentsTutor),
    path('student/appointments', views.allAppointmentsStudent),
    path('student/appointments/<str:tutor>/<str:state>/<str:className>/<str:time>', views.deleteNotification, name="deleteNotific"),
    path('tutor/appointments/<str:student>/<str:state>/<str:className>/<str:time>', views.deleteNotificationtutor, name="deleteNotifictutor"),


    path('tutor/profile', views.profile, name='profile'),
    path('tutor/profile/edit', views.edit_profile, name='edit_profile'),

    path('student/profile', views.profile, name='profile_student'),
    path('student/profile/edit', views.edit_profile, name='edit_profile_student'),






    path('StudentChat/<str:tutor>/<str:student>/', views.StudentChat, name='StudentChat'),
    path('TutorChat/<str:tutor>/<str:student>/', views.TutorChat, name='TutorChat'),
    path('student/StudentChatList/', views.chat_list, name='chat_list'),
    path('tutor/TutorChatList/', views.Tutor_chat_list, name='Tutor_chat_list'),


    path('canceltutor/<str:class_name>/<str:tutor>/<str:student>/', views.CancelTutor, name='cancel_tutor'),

    path('cancelstudent/<str:class_name>/<str:tutor>/<str:student>/', views.CancelStudent, name='cancel_student'),

    


    path('student/inbox', views.allMessagesStudent, name='student_messages'),
    path('tutor/inbox', views.allMessagesTutor, name='tutor_messages'),

]

