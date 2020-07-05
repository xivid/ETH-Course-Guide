#!/usr/bin/python3
from lxml import html
import requests
import re
import os

'''
    receives
        addr_format: URL to vvz.ethz.ch search result page, where the page ("seite") argument value is replaced by "{}", e.g. "http://vvz.ethz.ch/Vorlesungsverzeichnis/sucheLehrangebot.view?lerneinheitscode=&deptId=5&famname=&unterbereichAbschnittId=&seite={}&lerneinheitstitel=&rufname=&lehrsprache=&bereichAbschnittId=&semkez=2020S&studiengangAbschnittId=83713&studiengangTyp=MSC&ansicht=1&lang=en&katalogdaten=&wahlinfo="
        num_pages: total number of pages in this search result
    returns:  list of tuples (course_no, course_name)
'''
def get_list(addr_format, num_pages):
    courses = []  # list of tuples (course_no, course_name)
    for i in range(1, num_pages + 1):
        page = requests.get(addr_format.format(i))
        tree = html.fromstring(page.content)
        c = tree.xpath('//tr')
        d = [x for x in c if 'class' in x[0].attrib and x[0].attrib['class']=='border-no']
        courses += [(x[0][0].text, x[1][0][0].text) for x in d]
    return courses


'''
    converts the plain course name to a string with lower case letters and '-' only
'''
def sanitize_course_name(name):
    a = re.sub("[^a-z|A-Z|0-9|\ ]", "", name)
    b = re.sub("\ +", " ", a)
    return b.lower().replace(" ", "-")


'''
    requires:
        department name in lower case, e.g. "d-infk"
        list of tuples (course_no, course_name)
    returns:
        a string, including lines of Markdown code to be inserted into SUMMARY.md
'''
def summary_markdown(department, courses):
    s = ""
    for (no, name) in courses:
        s_name = sanitize_course_name(name)
        s += "  * [{}]({}/{}/README.md)\n".format(name, department, s_name)
    return s


def create_courses(department, courses, root_dir):
    department = department.lower()
    for (no, name) in courses:
        s_name = sanitize_course_name(name)
        new_dir = root_dir+"/{}/{}".format(department, s_name)
        if not os.path.isdir(new_dir):
            os.mkdir(new_dir)
            f = open(new_dir+"/README.md", "w")
            f.write("# {} {}".format(no, name))
            f.close()
            print("Created {} {} at {}".format(no, name, new_dir))


def merge_courses(courses_list):
    courses = []
    for x in courses_list:
        courses += x
    courses = list(set(courses))
    return sorted(courses,key=lambda x: x[1])