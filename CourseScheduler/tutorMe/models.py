from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models.signals import pre_delete
from django.dispatch import receiver


class tutorMeUser(models.Model):
    email = models.EmailField(unique=True)
    is_tutor = models.BooleanField(default=False)
    is_admin_set = models.BooleanField(default=False)
    first_name = models.CharField(default="", max_length=255)
    last_name = models.CharField(default="", max_length=255)
    phone_number = models.CharField(default="", max_length=20)
    preferred_contact = models.CharField(choices=[('phone', 'Phone'), ('email', 'Email')], default='email',
                                         max_length=10)

    # other fields as needed
    def __str__(self):
        return self.email


class TutorClasses(models.Model):
    tutor = models.ForeignKey('tutorMeUser', on_delete=models.CASCADE, )
    mnemonic = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    number = models.CharField(max_length=255, default="")


class Course(models.Model):
    course_name = models.CharField(default="", max_length=255)
    referenceLink = models.CharField(default="", max_length=100000)
    course_number = models.CharField(default="", max_length=1000)
    Subject = models.CharField(default="", max_length=4)


class Schedule(models.Model):
    tutor = models.ForeignKey('tutorMeUser', on_delete=models.CASCADE, )
    class_name = models.CharField(max_length=100)
    # start_time = models.DateTimeField()
    # end_time = models.DateTimeField()
    input_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    monday = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    tuesday = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    wednesday = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    thursday = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    friday = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    saturday = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    sunday = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)


class ScheduleStudent(models.Model):
    tutor = models.ForeignKey('tutorMeUser', related_name='tutor', on_delete=models.CASCADE, )
    student = models.ForeignKey('tutorMeUser', on_delete=models.CASCADE, )
    class_name = models.CharField(max_length=100)

    monday = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    tuesday = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    wednesday = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    thursday = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    friday = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    saturday = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    sunday = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)


class Appointment(models.Model):
    tutor = models.ForeignKey('tutorMeUser', on_delete=models.CASCADE, )
    student = models.ForeignKey('tutorMeUser', related_name='student', on_delete=models.CASCADE, )
    class_name = models.CharField(max_length=100)

    monday = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    tuesday = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    wednesday = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    thursday = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    friday = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    saturday = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)
    sunday = ArrayField(models.IntegerField(null=True, blank=True), null=True, blank=True)


class ChatMessage(models.Model):
    sender = models.ForeignKey('tutorMeUser', on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey('tutorMeUser', on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


from datetime import date, datetime


class Notification(models.Model):
    class requestState(models.TextChoices):
        ACC = 'Accepted',
        UND = 'Undecided',
        REJ = 'Rejected',
        CAN = 'Canceled'

    state = models.TextField(choices=requestState.choices)
    tutor = models.ForeignKey('tutorMeUser', related_name='notifyTutor', on_delete=models.CASCADE, )
    student = models.ForeignKey('tutorMeUser', related_name='notifyStudent', on_delete=models.CASCADE)
    class_name = models.CharField(max_length=100)
    time = models.DateTimeField(default=datetime.now, blank=True)

