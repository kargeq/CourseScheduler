import smtplib

from django.core.mail import send_mail
from django.db.models import Model, Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from datetime import datetime
from django.contrib import messages
from django.db.models import Model, Q, DateTimeField
from django.db.models.functions import Trunc
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import EditProfileForm
# def index(request):
#     return HttpResponse("Hello, world. You're at the tutorMe index.")
from tutorMe import Json
from tutorMe.Json import get_JSON_Subjects, Searchereds
from tutorMe.models import tutorMeUser, TutorClasses, ScheduleStudent, Notification
from django.shortcuts import render, redirect
from .forms import ScheduleForm, BugReportForm
import requests
from .models import Schedule, Appointment, ChatMessage
from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login
from django.urls import reverse
import traceback

from django.contrib.auth.models import AnonymousUser

from django.core.mail import send_mail
from django.conf import settings


def is_tutor(user):
    return tutorMeUser.objects.filter(email=user.email, is_tutor=True).exists()


def is_not_tutor(user):
    return tutorMeUser.objects.filter(email=user.email, is_tutor=False).exists()


def not_student(user):
    return not tutorMeUser.objects.filter(email=user.email, is_tutor=False).exists()


def not_tutor(user):
    return not tutorMeUser.objects.filter(email=user.email, is_tutor=True).exists()


def checkifTutor(request):
    if not isinstance(request.user, AnonymousUser):
        if not tutorMeUser.objects.filter(email=request.user.email, is_tutor=False).exists():
            return
        else:
            raise Http404()
    else:
        raise Http404()


def checkifStudent(request):
    if not isinstance(request.user, AnonymousUser):
        if not tutorMeUser.objects.filter(email=request.user.email, is_tutor=True).exists():
            return
        else:
            raise Http404()
    else:
        raise Http404()


class Index(TemplateView):
    template_name = "index.html"


def google_login(request):
    # Check if the user is already logged in
    if request.user.is_authenticated:
        return redirect('home')


@login_required
def tutor_check(request):
    if tutorMeUser.objects.filter(email=request.user.email, is_tutor=False).exists():
        return redirect('/tutorMe/student')

    if tutorMeUser.objects.filter(email=request.user.email, is_tutor=True).exists():
        return redirect('/tutorMe/tutor')

    return render(request, 'tutorCheck.html')


@login_required
@user_passes_test(not_student)
def TutorView(request):
    if not tutorMeUser.objects.filter(email=request.user.email, is_tutor=True).exists():
        newuser = tutorMeUser();
        newuser.email = request.user.email
        newuser.is_tutor = True
        newuser.first_name = request.user.first_name
        newuser.last_name = request.user.last_name
        newuser.save()

    if request.method == 'POST':
        initialSearchQuery = request.POST.get("searchBar")

        if initialSearchQuery:
            initialSearchResults = Searchereds(initialSearchQuery)
            return render(request, 'tutorMeTutorClasses.html', {'searchResults': initialSearchResults})
        else:
            return render(request, 'tutorMeTutor.html', )

    return render(request, 'tutorMeTutor.html')


def Tutor_Classes_View(request):
    checkifTutor(request)
    choice = request.POST.get("choice")
    classes = Json.get_classes(choice, "2023", "Spring")

    request.session[0] = choice
    return render(request, 'tutorMeTutorClasses.html', {'classes': classes})


def deleteClass(request, Class):
    checkifTutor(request)

    theEmail = request.user.email
    cur_user = tutorMeUser.objects.get(email=theEmail)

    mnemonic = Class.split(' ', 1)[0]
    namewithoutmneonic = Class.split(' ', 1)[1]
    query = TutorClasses.objects.filter(name=namewithoutmneonic, tutor_id=cur_user, mnemonic=mnemonic)
    if Schedule.objects.filter(tutor__email=theEmail, class_name=Class).exists():
        toBeDeleted = Schedule.objects.filter(tutor__email=theEmail, class_name=Class)
        toBeDeleted.delete()

    query.delete()

    return Tutor_Classes_List_View(request)


def searchView(request):
    checkifTutor(request)

    if request.method == 'POST':
        if request.POST.get("initialSearch"):
            searchQuery = request.POST.get("initialSearch")
        else:
            searchQuery = request.POST.get("searchBar")
        if searchQuery:
            searchResults = Searchereds(searchQuery)
        else:
            searchResults = []
        print(searchResults)

        for i in range(len(searchResults)):
            for j in range(len(searchResults[i])):
                if ("/" in str(searchResults[i][j])):
                    print(searchResults[i][j])
                    searchResults[i][j] = searchResults[i][j].replace("/", " ")  # print(searchResults)

    return render(request, 'tutorMeTutorClasses.html', {'searchResults': searchResults, 'slash': "%2F"})


def Tutor_Classes_List_View(request):
    checkifTutor(request)
    class_choice = request.POST.get("class_choice", "")

    theEmail = request.user.email
    cur_user = tutorMeUser.objects.get(email=request.user.email)
    if class_choice != "":
        mnemonic = request.session['0']

        if not TutorClasses.objects.filter(name=class_choice, tutor=cur_user).exists():
            newclass = TutorClasses();
            newclass.tutor = cur_user
            newclass.mnemonic = mnemonic
            newclass.name = class_choice
            newclass.save()

    query = TutorClasses.objects.filter(tutor=cur_user)

    list = []
    hasSchedule = []
    for i in query:
        otherarr = []
        curmneonic = i.mnemonic
        curname = i.name
        curmneonic += " "
        curmneonic += curname
        otherarr.append(curmneonic)
        print(curmneonic)
        if not Schedule.objects.filter(tutor__email=theEmail, class_name=curmneonic):
            otherarr.append(False)
        else:
            otherarr.append(True)
        list.append(otherarr)

    return render(request, 'TutorClassList.html', {'list': list})


def addClass(request, mnemonic, name, number):
    checkifTutor(request)
    cur_user = tutorMeUser.objects.get(email=request.user.email)
    # print(mnemonic)
    # print(name)
    # print(number)
    if not TutorClasses.objects.filter(name=name, tutor=cur_user).exists():
        newclass = TutorClasses();
        newclass.tutor = cur_user
        newclass.mnemonic = mnemonic
        newclass.name = name
        newclass.number = number
        newclass.save()
    return redirect(reverse('tutor_classes_list_view'))


@login_required
@user_passes_test(not_tutor)
def StudentView(request):
    if not tutorMeUser.objects.filter(email=request.user.email, is_tutor=False).exists():
        newuser = tutorMeUser();
        newuser.email = request.user.email
        newuser.is_tutor = False
        newuser.first_name = request.user.first_name
        newuser.last_name = request.user.last_name
        newuser.save()

    # items = get_JSON_Subjects("2023", "Spring");

    return render(request, 'tutorMeStudent.html')


def Student_Classes_View(request):
    checkifStudent(request)
    if request.method == 'POST':
        searchQuery = request.POST.get("searchBar")

        if searchQuery:
            searchResults = Searchereds(searchQuery)
        else:
            searchResults = []
    else:
        return render(request, 'tutorMeStudentClasses.html')

    for i in range(len(searchResults)):
        for j in range(len(searchResults[i])):
            if ("/" in str(searchResults[i][j])):
                print(searchResults[i][j])
                searchResults[i][j] = searchResults[i][j].replace("/", " ")

    return render(request, 'tutorMeStudentClasses.html', {'searchResults': searchResults})


def Student_Classes_List_View(request, mnemonic, name, number):
    checkifStudent(request)
    both = mnemonic + " " + name
    query = TutorClasses.objects.filter(name=name)
    list = []
    for i in query:
        tutor = i.tutor
        if (Schedule.objects.filter(tutor=tutor, class_name=both).exists()):
            info = []
            first = tutor.first_name
            last = tutor.last_name
            full_name = first + " " + last
            info.append(full_name)
            info.append(Schedule.objects.get(tutor=tutor, class_name=both).input_rate)
            list.append(info)

    return render(request, 'StudentClassList.html', {'list': list, 'name': name, 'mnemonic': mnemonic})


def schedule_view(request, name):
    checkifTutor(request)
    return render(request, 'tutorSchedule.html', {'name': name})


def calendar_times(request, class_name):
    if request.method == "POST":
        tutor = tutorMeUser.objects.get(email=request.user.email)
        schedule, created = Schedule.objects.get_or_create(tutor=tutor, class_name=class_name,

                                                           )
        schedule.input_rate = request.POST.get('inputRate')
        m = []
        tu = []
        w = []
        th = []
        f = []
        sa = []
        su = []

        for button_name in request.POST.getlist("checkbox"):
            if button_name.startswith('m'):
                m.append(int(button_name[1:]))
            elif button_name.startswith('tu'):
                tu.append(int(button_name[2:]))
            elif button_name.startswith('w'):
                w.append(int(button_name[1:]))
            elif button_name.startswith('th'):
                th.append(int(button_name[2:]))
            elif button_name.startswith('f'):
                f.append(int(button_name[1:]))
            elif button_name.startswith('sa'):
                sa.append(int(button_name[2:]))
            elif button_name.startswith('su'):
                su.append(int(button_name[2:]))

        schedule.monday = m
        schedule.tuesday = tu
        schedule.wednesday = w
        schedule.thursday = th
        schedule.friday = f
        schedule.saturday = sa
        schedule.sunday = su

        schedule.save()

    return redirect(reverse('tutor_classes_list_view'))


def EditClass(request, name):
    checkifTutor(request)

    query = Schedule.objects.get(class_name=name, tutor__email=request.user.email)
    mon = query.monday
    tues = query.tuesday
    wed = query.wednesday
    thurs = query.thursday
    fri = query.friday
    sat = query.saturday
    sun = query.sunday
    rate = query.input_rate
    prev = [mon, tues, wed, thurs, fri, sat, sun, rate]

    return render(request, 'TutorEdit.html', {'name': name, 'prev': prev})


def StudentMakeSchedule(request, tutor, name, mnemonic):
    checkifStudent(request)
    if " " in tutor:
        tutor_name = tutor.split(' ')
        query = tutorMeUser.objects.get(is_tutor=True, first_name=tutor_name[0], last_name=tutor_name[1])
    else:
        query = tutorMeUser.objects.get(is_tutor=True, first_name=tutor)

    full_name = mnemonic + " " + name

    tutor_schedule = Schedule.objects.get(class_name=full_name, tutor_id=query.id)
    mon_filtered = []
    tues_filtered = []
    wen_filtered = []
    thurs_filtered = []
    fri_filtered = []
    sat_filtered = []
    sun_filtered = []

    Mon_set = set()
    Tue_set = set()
    Wed_set = set()
    Thur_set = set()
    Fri_set = set()
    Sat_set = set()
    Sun_set = set()

    for obj in Appointment.objects.filter(class_name=full_name, tutor_id=query.id):
        Mon_set.update(set(obj.monday))

        Tue_set.update(set(obj.tuesday))
        Wed_set.update(set(obj.wednesday))
        Thur_set.update(set(obj.thursday))
        Fri_set.update(set(obj.friday))
        print(Fri_set)
        Sat_set.update(set(obj.saturday))
        Sun_set.update(set(obj.sunday))
    for val in tutor_schedule.monday:

        if val not in Mon_set:
            mon_filtered.append(val)
    for val in tutor_schedule.tuesday:
        if val not in Tue_set:
            tues_filtered.append(val)
    for val in tutor_schedule.wednesday:
        if val not in Wed_set:
            wen_filtered.append(val)
    for val in tutor_schedule.thursday:
        if val not in Thur_set:
            thurs_filtered.append(val)
    for val in tutor_schedule.friday:
        if val not in Fri_set:
            fri_filtered.append(val)
    for val in tutor_schedule.saturday:
        if val not in Sat_set:
            sat_filtered.append(val)
    for val in tutor_schedule.sunday:
        if val not in Sun_set:
            sun_filtered.append(val)
    # FIX THIS:  newMon=[item for item in tutor_schedule.monday if item not in ScheduleStudent.objects.get(tutor=tutor)] #check array of each object
    mon = mon_filtered
    tues = tues_filtered
    wed = wen_filtered
    thurs = thurs_filtered
    fri = fri_filtered
    sat = sat_filtered
    sun = sun_filtered
    rate = tutor_schedule.input_rate
    tutor_schedule = [mon, tues, wed, thurs, fri, sat, sun, rate]

    return render(request, 'Student_Make_Schedule.html',
                  {'tutor': tutor, 'name': name, 'mnemonic': mnemonic, 'tutor_schedule': tutor_schedule})


def calendarStudent(request, tutor, name, mnemonic):
    checkifStudent(request)
    split = tutor.split(" ")
    first_name = split[0]
    last_name = split[1]

    full_name = mnemonic + " " + name
    if request.method == "POST":
        student = tutorMeUser.objects.get(email=request.user.email)
        tutor = tutorMeUser.objects.get(first_name=first_name, last_name=last_name, is_tutor=True)
        schedule, created = ScheduleStudent.objects.get_or_create(
            student=student,
            tutor=tutor,
            class_name=full_name,
        )

        m = []
        tu = []
        w = []
        th = []
        f = []
        sa = []
        su = []

        for button_name in request.POST.getlist("checkbox"):
            if button_name.startswith('m'):
                m.append(int(button_name[1:]))
            elif button_name.startswith('tu'):
                tu.append(int(button_name[2:]))
            elif button_name.startswith('w'):
                w.append(int(button_name[1:]))
            elif button_name.startswith('th'):
                th.append(int(button_name[2:]))
            elif button_name.startswith('f'):
                f.append(int(button_name[1:]))
            elif button_name.startswith('sa'):
                sa.append(int(button_name[2:]))
            elif button_name.startswith('su'):
                su.append(int(button_name[2:]))

        schedule.monday = m
        schedule.tuesday = tu
        schedule.wednesday = w
        schedule.thursday = th
        schedule.friday = f
        schedule.saturday = sa
        schedule.sunday = su

        schedule.save()

    return redirect(reverse('student_default'))


def tutorRequests(request):
    checkifTutor(request)
    tutor = tutorMeUser.objects.get(email=request.user.email)

    query = ScheduleStudent.objects.filter(tutor=tutor)
    list = []
    for i in query:
        each = []
        each.append(i.class_name)

        firstT = tutor.first_name
        lastT = tutor.last_name
        full_nameT = firstT + " " + lastT
        each.append(full_nameT)

        student = i.student
        first = student.first_name
        last = student.last_name
        full_name = first + " " + last
        each.append(full_name)

        def time_slots(times):
            slots = []
            for i in range(len(times)):
                start = times[i]
                end = times[i] + 1
                am_pm_start = "am"
                am_pm_end = "am"
                if start >= 12:
                    am_pm_start = "pm"
                    if start > 12:
                        start -= 12
                if end >= 12:
                    am_pm_end = "pm"
                    if end > 12:
                        end -= 12
                slots.append(f"{start}-{end}{am_pm_start}")
            return ", ".join(slots)

        each.append(time_slots(i.monday))
        each.append(time_slots(i.tuesday))
        each.append(time_slots(i.wednesday))
        each.append(time_slots(i.thursday))
        each.append(time_slots(i.friday))
        each.append(time_slots(i.saturday))
        each.append(time_slots(i.sunday))
        list.append(each)
    return render(request, 'tutorRequests.html', {'list': list})


def generateRejectionMsgToStudent(student, tutor, class_name):
    """

    :param app:
    """
    print('WORKING Rejecion')
    msg = Notification.objects.create(state=Notification.requestState.REJ, tutor=tutor, student=student,
                                      class_name=class_name)
    msg.save()


def generateAcceptanceMsgToStudent(student, tutor, class_name):
    """

    :param app:
    """
    print('WORKING Acceptance')
    msg = Notification.objects.create(state=Notification.requestState.ACC, tutor=tutor, student=student,
                                      class_name=class_name)
    msg.save()


def deleteNotification(request, state, tutor, className, time):
    theEmail = request.user.email
    student = tutorMeUser.objects.get(email=theEmail)

    if  Notification.objects.filter(state=state, tutor__email=tutor, student=student,
                                              class_name=className, time=time).exists:
        toBeDeleted = Notification.objects.filter(state=state, tutor__email=tutor, student=student,
                                                  class_name=className, time=time)

        toBeDeleted.delete()




    return allMessagesStudent(request)

def deleteNotificationtutor(request, student, state, className, time):
    theEmail = request.user.email
    tutor = tutorMeUser.objects.get(email=theEmail)
    toBeDeleted=Notification.objects.get(state=state, tutor=tutor,
                                      class_name=className, time=time)
    if (Notification.objects.filter(state=state, tutor=tutor,
                                           class_name=className, time=time).exists):
        toBeDeleted = Notification.objects.get(state=state, tutor=tutor,
                                               class_name=className, time=time)
        toBeDeleted.delete()
    return allMessagesTutor(request)

def studentRequests(request):
    checkifStudent(request)
    student = tutorMeUser.objects.get(email=request.user.email)

    query = ScheduleStudent.objects.filter(student=student)
    list = []
    for i in query:
        each = []
        each.append(i.class_name)

        tutor = i.tutor
        firstT = tutor.first_name
        lastT = tutor.last_name
        full_nameT = firstT + " " + lastT
        each.append(full_nameT)

        first = student.first_name
        last = student.last_name
        full_name = first + " " + last
        each.append(full_name)

        def time_slots(times):
            slots = []
            for i in range(len(times)):
                start = times[i]
                end = times[i] + 1
                am_pm_start = "am"
                am_pm_end = "am"
                if start >= 12:
                    am_pm_start = "pm"
                    if start > 12:
                        start -= 12
                if end >= 12:
                    am_pm_end = "pm"
                    if end > 12:
                        end -= 12
                slots.append(f"{start}-{end}{am_pm_start}")
            return ", ".join(slots)

        each.append(time_slots(i.monday))
        each.append(time_slots(i.tuesday))
        each.append(time_slots(i.wednesday))
        each.append(time_slots(i.thursday))
        each.append(time_slots(i.friday))
        each.append(time_slots(i.saturday))
        each.append(time_slots(i.sunday))
        list.append(each)
    return render(request, 'studentRequests.html', {'list': list})


def accepted(request, class_name, tutor, student):
    split_tutor = tutor.split()
    tutor_first = split_tutor[0]
    tutor_last = split_tutor[1]
    tutor_name = tutorMeUser.objects.get(first_name=tutor_first, last_name=tutor_last, is_tutor=True)

    split_student = student.split()
    student_first = split_student[0]
    student_last = split_student[1]
    student_name = tutorMeUser.objects.get(first_name=student_first, last_name=student_last, is_tutor=False)

    x = ScheduleStudent.objects.get(class_name=class_name, tutor=tutor_name, student=student_name)

    generateAcceptanceMsgToStudent(tutor=tutor_name, student=student_name, class_name=class_name)

    apt = Appointment.objects.create(student=x.student, tutor=x.tutor, class_name=x.class_name, )
    apt.monday = x.monday
    apt.tuesday = x.tuesday
    apt.wednesday = x.wednesday
    apt.thursday = x.thursday
    apt.friday = x.friday
    apt.saturday = x.saturday
    apt.sunday = x.saturday
    apt.save()

    x.delete()

    return tutorRequests(request)


def deleteRequest(request, class_name, tutor, student):
    splitTutor = tutor.split(" ")
    first_nameT = splitTutor[0]
    last_nameT = splitTutor[1]
    tutor1 = tutorMeUser.objects.get(first_name=first_nameT, last_name=last_nameT, is_tutor=True)

    splitStudent = student.split(" ")
    first_nameS = splitStudent[0]
    last_nameS = splitStudent[1]

    student1 = tutorMeUser.objects.get(first_name=first_nameS, last_name=last_nameS, is_tutor=False)
    toBeDeleted = ScheduleStudent.objects.filter(tutor=tutor1, student=student1, class_name=class_name, )
    generateRejectionMsgToStudent(tutor=tutor1, student=student1, class_name=class_name)
    toBeDeleted.delete()

    return tutorRequests(request)


def CancelTutor(request, class_name, tutor, student):
    checkifTutor(request)
    splitTutor = tutor.split(" ")
    first_nameT = splitTutor[0]
    last_nameT = splitTutor[1]
    tutor1 = tutorMeUser.objects.get(first_name=first_nameT, last_name=last_nameT, is_tutor=True)

    splitStudent = student.split(" ")
    first_nameS = splitStudent[0]
    last_nameS = splitStudent[1]

    student1 = tutorMeUser.objects.get(first_name=first_nameS, last_name=last_nameS, is_tutor=False)
    toBeDeleted = Appointment.objects.filter(tutor=tutor1, student=student1, class_name=class_name)
    toBeDeleted.delete()

    msg = Notification.objects.create(state=Notification.requestState.CAN, tutor=tutor1, student=student1,
                                      class_name=class_name)
    msg.save()

    return allAppointmentsTutor(request)


def CancelStudent(request, class_name, tutor, student):
    checkifStudent(request)
    splitTutor = tutor.split(" ")
    first_nameT = splitTutor[0]
    last_nameT = splitTutor[1]
    tutor1 = tutorMeUser.objects.get(first_name=first_nameT, last_name=last_nameT, is_tutor=True)

    splitStudent = student.split(" ")
    first_nameS = splitStudent[0]
    last_nameS = splitStudent[1]

    student1 = tutorMeUser.objects.get(first_name=first_nameS, last_name=last_nameS, is_tutor=False)
    toBeDeleted = Appointment.objects.filter(tutor=tutor1, student=student1, class_name=class_name)
    toBeDeleted.delete()

    msg = Notification.objects.create(state=Notification.requestState.CAN, tutor=tutor1, student=student1,
                                      class_name=class_name)
    msg.save()

    return allAppointmentsStudent(request)


def allAppointmentsTutor(request):
    checkifTutor(request)
    tutor = tutorMeUser.objects.get(email=request.user.email)

    query = Appointment.objects.filter(tutor=tutor)
    list = []
    for i in query:
        each = []
        each.append(i.class_name)

        firstT = tutor.first_name
        lastT = tutor.last_name
        full_nameT = firstT + " " + lastT
        each.append(full_nameT)

        student = i.student
        first = student.first_name
        last = student.last_name
        full_name = first + " " + last
        each.append(full_name)

        def time_slots(times):
            slots = []
            for i in range(len(times)):
                start = times[i]
                end = times[i] + 1
                am_pm_start = "am"
                am_pm_end = "am"
                if start >= 12:
                    am_pm_start = "pm"
                    if start > 12:
                        start -= 12
                if end >= 12:
                    am_pm_end = "pm"
                    if end > 12:
                        end -= 12
                slots.append(f"{start}-{end}{am_pm_start}")
            return ", ".join(slots)

        each.append(time_slots(i.monday))
        each.append(time_slots(i.tuesday))
        each.append(time_slots(i.wednesday))
        each.append(time_slots(i.thursday))
        each.append(time_slots(i.friday))
        each.append(time_slots(i.saturday))
        each.append(time_slots(i.sunday))
        list.append(each)
    return render(request, 'appointmentsTutor.html', {'list': list})


def allAppointmentsStudent(request):
    checkifStudent(request)
    student = tutorMeUser.objects.get(email=request.user.email)

    query = Appointment.objects.filter(student=student)
    list = []
    for i in query:
        each = []
        each.append(i.class_name)

        tutor = i.tutor
        firstT = tutor.first_name
        lastT = tutor.last_name
        full_nameT = firstT + " " + lastT
        each.append(full_nameT)

        first = student.first_name
        last = student.last_name
        full_name = first + " " + last
        each.append(full_name)

        def time_slots(times):
            slots = []
            for i in range(len(times)):
                start = times[i]
                end = times[i] + 1
                am_pm_start = "am"
                am_pm_end = "am"
                if start >= 12:
                    am_pm_start = "pm"
                    if start > 12:
                        start -= 12
                if end >= 12:
                    am_pm_end = "pm"
                    if end > 12:
                        end -= 12
                slots.append(f"{start}-{end}{am_pm_start}")
            return ", ".join(slots)

        each.append(time_slots(i.monday))
        each.append(time_slots(i.tuesday))
        each.append(time_slots(i.wednesday))
        each.append(time_slots(i.thursday))
        each.append(time_slots(i.friday))
        each.append(time_slots(i.saturday))
        each.append(time_slots(i.sunday))
        list.append(each)
    return render(request, 'appointmentsStudent.html', {'list': list})


def profile(request):
    user = request.user
    istutor = is_tutor(user)
    print(istutor)

    cur_user = tutorMeUser.objects.get(email=request.user.email)
    first = cur_user.first_name
    last = cur_user.last_name
    phone = cur_user.phone_number
    contact = cur_user.preferred_contact

    return render(request, 'view_profile.html',
                  {'user': user, 'istutor': istutor, "phone": phone, 'contact': contact, 'first': first, "last": last})


def edit_profile(request):
    user = request.user
    istutor = is_tutor(user)
    cur_user = tutorMeUser.objects.get(email=request.user.email)

    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=cur_user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=cur_user)

    first = cur_user.first_name
    last = cur_user.last_name
    phone = cur_user.phone_number
    contact = cur_user.preferred_contact

    context = {'form': form, 'istutor': istutor, 'user': user, "phone": phone, 'contact': contact, 'first': first,
               "last": last}
    return render(request, 'edit_profile.html', context)


def StudentChat(request, tutor, student):
    checkifStudent(request)
    student_sender = tutorMeUser.objects.get(email=request.user.email)

    splitStudent = student.split(" ")
    first_nameS = splitStudent[0]
    last_nameS = splitStudent[1]
    student_user = tutorMeUser.objects.get(first_name=first_nameS, last_name=last_nameS, is_tutor=False)

    splitTutor = tutor.split(" ")
    first_nameT = splitTutor[0]
    last_nameT = splitTutor[1]
    tutor_user = tutorMeUser.objects.get(first_name=first_nameT, last_name=last_nameT, is_tutor=True)

    messages = ChatMessage.objects.filter(sender=student_user, receiver=tutor_user) | ChatMessage.objects.filter(
        sender=tutor_user, receiver=student_user)

    context = {'user': student_user, 'other_user': tutor, 'messages': messages, }
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            ChatMessage.objects.create(sender=student_user, receiver=tutor_user, content=content)
            return redirect('StudentChat', tutor=tutor, student=student)
    return render(request, 'StudentChat.html', context)


def TutorChat(request, tutor, student):
    checkifTutor(request)
    tutor_sender = tutorMeUser.objects.get(email=request.user.email)

    splitStudent = student.split(" ")
    first_nameS = splitStudent[0]
    last_nameS = splitStudent[1]
    student_user = tutorMeUser.objects.get(first_name=first_nameS, last_name=last_nameS, is_tutor=False)

    splitTutor = tutor.split(" ")
    first_nameT = splitTutor[0]
    last_nameT = splitTutor[1]
    tutor_user = tutorMeUser.objects.get(first_name=first_nameT, last_name=last_nameT, is_tutor=True)

    messages = ChatMessage.objects.filter(sender=tutor_user, receiver=student_user) | ChatMessage.objects.filter(
        sender=student_user, receiver=tutor_user)
    context = {'user': tutor_user, 'other_user': student, 'messages': messages, }

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            ChatMessage.objects.create(sender=tutor_user, receiver=student_user, content=content)
            return redirect('TutorChat', tutor=tutor, student=student)
    return render(request, 'TutorChat.html', context)


def chat_list(request):
    student = tutorMeUser.objects.get(email=request.user.email)
    student_name = student.first_name + " " + student.last_name
    chats = ChatMessage.objects.filter(sender=student) | ChatMessage.objects.filter(receiver=student)
    unique_chats = []
    unique_names = []
    for chat in chats:
        if chat.sender == student:
            if chat.receiver not in unique_chats:
                tutor_name = chat.receiver.first_name + " " + chat.receiver.last_name
                unique_chats.append(chat.receiver)
                unique_names.append(tutor_name)
        elif chat.receiver == student:
            if chat.sender not in unique_chats:
                tutor_name = chat.sender.first_name + " " + chat.sender.last_name
                unique_chats.append(chat.sender)
                unique_names.append(tutor_name)

    return render(request, 'StudentChat_list.html', {'unique_names': unique_names, 'student_name': student_name})


def Tutor_chat_list(request):
    checkifTutor(request)
    tutor = tutorMeUser.objects.get(email=request.user.email)
    tutor_name = tutor.first_name + " " + tutor.last_name
    chats = ChatMessage.objects.filter(sender=tutor) | ChatMessage.objects.filter(receiver=tutor)
    unique_chats = []
    unique_names = []
    for chat in chats:
        if chat.sender == tutor:
            if chat.receiver not in unique_chats:
                student_name = chat.receiver.first_name + " " + chat.receiver.last_name
                unique_chats.append(chat.receiver)
                unique_names.append(student_name)
        elif chat.receiver == tutor:
            if chat.sender not in unique_chats:
                student_name = chat.sender.first_name + " " + chat.sender.last_name
                unique_chats.append(chat.sender)
                unique_names.append(student_name)

    return render(request, 'TutorChat_list.html', {'unique_names': unique_names, 'tutor_name': tutor_name})


def page_not_found_view(request, exception):
    return render(request, '404.html',
                  status=404)  # taken from https://levelup.gitconnected.com/django-customize-404-error-page-72c6b6277317


def send_to_home(request):
    if not isinstance(request.user, AnonymousUser):
        Curr_user = tutorMeUser.objects.get(email=request.user.email)
        if Curr_user.is_tutor:
            return redirect("tutor")
        else:
            return redirect("student_default")
    else:
        return redirect("index")


@login_required
def bug_report_view(request):
    name = tutorMeUser.objects.get(email=request.user.email)
    if request.method == 'POST':
        form = BugReportForm(request.POST)
        if form.is_valid():

            fullName = name.first_name + " " + name.last_name
            email = name.email
            bug_description = form.cleaned_data['bug_description']
            message = f"{fullName} with email: ({email}) has reported a bug: {bug_description}"

            send_mail(f"Bug report by {fullName}", message, "settings.EMAIL_HOST_USER", ["errorsherokututor@gmail.com"],
                      fail_silently=False)
            if name.is_tutor:
                messages.success(request, 'Form submitted successfully!')
                return redirect("tutor")
            else:
                messages.success(request, 'Form submitted successfully!')
                return redirect("student_default")

    else:
        form = BugReportForm()
    return render(request, 'bug_report.html', {'form': form, "name": name})


@login_required
@user_passes_test(is_not_tutor)
def allMessagesStudent(request):
    student = tutorMeUser.objects.get(email=request.user.email)

    notifications = Notification.objects.filter(student=student).order_by('-time')

    msgs = []
    for n in notifications:
        msg = []

        # print("State: ", n.state, " Tutor: ", n.tutor.first_name, " ClassName: ", n.class_name)

        if n.state == "Rejected":
            msg.append("Rejected")
        elif n.state == "Accepted":
            msg.append("Accepted")
        elif n.state == "Canceled":
            msg.append("Canceled")

        fullName = n.tutor.first_name + ' ' + n.tutor.last_name
        msg.append(fullName)
        msg.append(n.class_name)
        timeStr = ' at ' + str(n.time)[11:16] + ' on ' + str(n.time)[:10]
        msg.append(timeStr)
        msg.append(n.tutor)
        msg.append(n.time)
        msgs.append(msg)

    return render(request, 'inboxStudent.html', {'msgs': msgs})


@login_required
@user_passes_test(is_tutor)
def allMessagesTutor(request):
    tutor = tutorMeUser.objects.get(email=request.user.email)

    notifications = Notification.objects.filter(tutor=tutor).order_by('-time')


    msgs = []
    for n in notifications:
        msg = []


        # print("State: ", n.state, " Tutor: ", n.tutor.first_name, " ClassName: ", n.class_name)

        if n.state == "Rejected":
            msg.append("Rejected")
            print("Rejected")
        elif n.state == "Accepted":
            msg.append("Accepted")
            print("Accepted")
        elif n.state == "Canceled":
            msg.append("Canceled")
            print("Canceled")

        fullName = n.student.first_name + ' ' + n.student.last_name

        msg.append(fullName)
        msg.append(n.class_name)
        timeStr = ' at ' + str(n.time)[11:16] + ' on ' + str(n.time)[:10]
        msg.append(timeStr)

        msg.append(n.student)
        msg.append(n.time)
        msgs.append(msg)

    return render(request, 'inboxTutor.html', {'msgs': msgs})

