from django.test import TestCase
from .models import tutorMeUser, Schedule, ScheduleStudent, ChatMessage
from .views import TutorView, StudentView
from django.urls import reverse

# Create your tests here.

class userTest(TestCase):

    def create_user(self):
        user = tutorMeUser.objects.create()
        user.save()
        return user

    def test_userCreated(self):
        x = self.create_user()
        self.assertTrue(isinstance(x, tutorMeUser))

    def test_userStudent(self):
        x = self.create_user()
        self.assertEqual(x.is_tutor, False)

    def test_userTutorAttributes(self):
        x = tutorMeUser(email='1234@gmail.com', first_name='john', last_name='doe', is_tutor=True)
        self.assertEqual(x.is_tutor, True)
        self.assertEqual(x.email, '1234@gmail.com')
        self.assertEqual(x.first_name, 'john')
        self.assertEqual(x.last_name, 'doe')

    def test_userTutorPhoneNumberContact(self):
        x = tutorMeUser(email='1234@gmail.com', first_name='john', last_name='doe', phone_number='123-456-789',
                            preferred_contact='phone', is_tutor=True)
        self.assertEqual(x.is_tutor, True)
        self.assertEqual(x.email, '1234@gmail.com')
        self.assertEqual(x.first_name, 'john')
        self.assertEqual(x.last_name, 'doe')
        self.assertEqual(x.phone_number, '123-456-789')
        self.assertEqual(x.preferred_contact, 'phone')

    def test_tutorSchedule(self):
        x = tutorMeUser(email='1234@gmail.com', first_name='john', last_name='doe', phone_number='123-456-789',
                            preferred_contact='phone', is_tutor=True)
        sch = Schedule( tutor=x, class_name="CS Advanced Software Development Techniques", input_rate=15, monday=[1, 2, 3] )

        self.assertEqual(sch.monday, [1, 2, 3])

    def test_defaultRate(self):
        x = tutorMeUser(email='1234@gmail.com', first_name='john', last_name='doe', phone_number='123-456-789',
                            preferred_contact='phone', is_tutor=True)
        sch = Schedule( tutor=x, class_name="CS Advanced Software Development Techniques" )

        self.assertEqual(sch.input_rate, 0)

    def test_correctClass(self):
        x = tutorMeUser(email='1234@gmail.com', first_name='john', last_name='doe', phone_number='123-456-789',
                            preferred_contact='phone', is_tutor=True)
        sch = Schedule( tutor=x, class_name="CS Advanced Software Development Techniques" )

        self.assertEqual(sch.class_name, "CS Advanced Software Development Techniques")

    def test_studentScheduleNoTimes(self):
        tutor = tutorMeUser(email='1234@gmail.com', first_name='john', last_name='doe', phone_number='123-456-7891',
                            preferred_contact='phone', is_tutor=True)
        student = tutorMeUser(email='5678@gmail.com', first_name='jane', last_name='doe', phone_number='000-000-0000',
                            preferred_contact='phone', is_tutor=False)
        sch = ScheduleStudent( tutor=tutor, student=student, class_name="CS Advanced Software Development Techniques")

        self.assertEqual(sch.class_name, "CS Advanced Software Development Techniques")
        self.assertEqual(sch.monday, None)
        self.assertEqual(sch.tuesday, None)
        self.assertEqual(sch.wednesday, None)
        self.assertEqual(sch.thursday, None)
        self.assertEqual(sch.friday, None)
        self.assertEqual(sch.saturday, None)
        self.assertEqual(sch.sunday, None)

    def test_studentScheduleTimes(self):
        tutor = tutorMeUser(email='1234@gmail.com', first_name='john', last_name='doe', phone_number='123-456-7891',
                            preferred_contact='phone', is_tutor=True)
        student = tutorMeUser(email='5678@gmail.com', first_name='jane', last_name='doe', phone_number='000-000-0000',
                            preferred_contact='phone', is_tutor=False)
        sch = ScheduleStudent( tutor=tutor, student=student, class_name="CS Advanced Software Development Techniques",
                               monday=[1, 2, 3], wednesday=[8, 9])

        self.assertEqual(sch.class_name, "CS Advanced Software Development Techniques")
        self.assertEqual(sch.monday, [1, 2, 3])
        self.assertEqual(sch.tuesday, None)
        self.assertEqual(sch.wednesday, [8, 9])
        self.assertEqual(sch.thursday, None)
        self.assertEqual(sch.friday, None)
        self.assertEqual(sch.saturday, None)
        self.assertEqual(sch.sunday, None)

    def test_chat(self):
        tutor = tutorMeUser(email='1234@gmail.com', first_name='john', last_name='doe', phone_number='123-456-7891',
                            preferred_contact='phone', is_tutor=True)
        student = tutorMeUser(email='5678@gmail.com', first_name='jane', last_name='doe', phone_number='000-000-0000',
                            preferred_contact='phone', is_tutor=False)

        c = ChatMessage(sender=tutor, receiver=student, content="hi, i am a tutor, how are you?")

        self.assertEqual(c.content, "hi, i am a tutor, how are you?")

    def test_chatSenderRec(self):
        tutor = tutorMeUser(email='1234@gmail.com', first_name='john', last_name='doe', phone_number='123-456-7891',
                            preferred_contact='phone', is_tutor=True)
        student = tutorMeUser(email='5678@gmail.com', first_name='jane', last_name='doe', phone_number='000-000-0000',
                            preferred_contact='phone', is_tutor=False)

        c = ChatMessage(sender=tutor, receiver=student, content="hi, i am a tutor, how are you?")

        self.assertEqual(c.sender.first_name, 'john')
        self.assertEqual(c.receiver.first_name, 'jane')


# class viewsTest(TestCase):
#
#     def test_tutorView(self):
#         # x = self.create_user()
#         # y = self.client.get(url)
#         # self.assertEqual(y.status_code, 200)
#         # self.assertIn(x.title, y.content)
#         path = reverse("tutorMe:tutor")
#         request = RequestFactory().get(path)
#         response = TutorView(request)
#         assert response.status_code == 200