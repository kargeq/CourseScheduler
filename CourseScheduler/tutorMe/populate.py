import requests
from tutorMe.models import Course
import time
def Searcher():
    data = 1
    page_num = 84
    year ="23"
    semester = "2"
    relevant_attrs = ['catalog_nbr', 'descr', 'subject']
    while data:
        print(page_num)
        page_num_str = str(page_num)
        url = "https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01&term=1"
        year_sem_num = year + semester
        url += year_sem_num
        url += "&page="
        url += page_num_str
        try:
            r = requests.get(url)
        except:
            print("at page number"+str(page_num))
            time.sleep(5)
            continue
        data = r.json()
        for index in data :
            if not Course.objects.filter(course_name=index["descr"]).exists(): #if updating databse you should have a set and see if in set and remove this line
                newCourse=Course()
                newCourse.course_name=index["descr"]
                newCourse.Subject=index["subject"]
                newCourse.course_number=index["catalog_nbr"]
                newCourse.referenceLink=url+"&class_nbr="+str(index["class_nbr"])
                newCourse.save()
        page_num += 1
print(Searcher())