import datetime
from bs4 import BeautifulSoup
import os
import csv
from matplotlib.pyplot import savefig
from matplotlib import pyplot
import sys

if len(sys.argv)<2:
    print('Usage: %s path/to/moduleoverview.aspx\n  (download file from '
          'https://vunet.login.vu.nl/Pages/SelfServices/Study/moduleoverview.aspx)' % sys.argv[0])
    exit()
else:
    source_path = sys.argv[1]
    if not source_path.split('/')[-1] == 'moduleoverview.aspx':
        # maybe you renamed it, that's ok
        pass
    if not os.path.isfile(source_path):
        print("%s not found" % source_path)
        exit()

ALSO_PLOT_STUFF = True

# don't change these
COURSE_NAME = 'Course name (in alphabetic order)'
COURSE_CODE = 'Course code'
GRADE_DATE = 'Examination Date'
CREDITS = 'EC'
GRADE = 'grade'

##########################
### Personal configuration
#### (change them)
##########################

NAME = '<name>'
STUDENT_NUMBER = '<vunet id>'
PROGRAMME = '<programme name>'
LEVEL = 'Bachelor' # or 'Master'

MINOR_NAME = '<minor programme name>'
MINOR_UNI_NAME = '<name of uni that facilitated your minor>'

# course codes for your minor subjects
MINORS = [
    'X_400001',
    'X_400002',
    'X_400003'
]

# courses you plan on taking in the future, or courses you've taken but which didn't make it through the system yet
FUTURE = [
    {
        COURSE_NAME: 'Course Name',
        COURSE_CODE: 'X_400004',
        CREDITS: 6,
        GRADE_DATE: '31-01-2018'
    },
    {
        COURSE_NAME: 'Other Course',
        COURSE_CODE: 'X_400005',
        CREDITS: 6,
        GRADE_DATE: '31-03-2018'
    }
]

#############################
### Don't change anything below
#############################



# column headers in required form
FORM_NAME = 'Academic Profile %s.xls' % LEVEL

with open(source_path) as f:
    soup = BeautifulSoup(f.read(), 'lxml')

INDICES = {
    COURSE_NAME: 0,
    COURSE_CODE: 1,
    # PERIOD: 2, # irrelevant
    GRADE_DATE: 3,
    CREDITS: 4,
    GRADE: 5  # irrelevant
}

HEADER_ROW = ['No.', COURSE_NAME, COURSE_NAME, CREDITS, GRADE_DATE]

results = []
for row in [r for r in soup.find_all('tr', {'class': 'passed'})]:
    values = [i.string for i in row.find_all('td')]
    if int(values[INDICES[CREDITS]]) > 0:
        results.append({key: values[INDICES[key]].replace(',', '.') for key in INDICES})


def totimestamp(x):
    return datetime.datetime.strptime(x[GRADE_DATE], "%d-%m-%Y").timestamp()


def deleted_dup():
    for r1 in range(len(results)):
        for r2 in range(r1 + 1, len(results)):
            if results[r1][COURSE_NAME] == results[r2][COURSE_NAME]:
                # keep the one with highest grade, if passed the same course more than once
                results.pop(r1 if results[r1][GRADE] < results[r2][GRADE] else r2)
                return True
    return False


while deleted_dup():
    pass

grades = [float(i[GRADE]) for i in results]
times = [totimestamp(i) for i in results]

results = sorted(results + FUTURE, key=totimestamp)

academic_years = {}

while len(results) > 0:

    result = results.pop(0)
    first_date = result[GRADE_DATE]
    day, month, year = first_date.split('-')
    if int(month) < 9:
        # spring semester
        academic_year = str(int(year) - 1) + '-' + year
    else:
        academic_year = year + '-' + str(int(year) + 1)
    if academic_year not in academic_years:
        academic_years[academic_year] = []
    academic_years[academic_year].append(result)

starting_year = int(sorted(academic_years)[0].split('-')[0])

first_rows = [
    ['Name: ', NAME],
    ['Studentnumber:', STUDENT_NUMBER],
    ['Programme:', PROGRAMME],
    ['Starting year of the programme:', starting_year]
]

with open(FORM_NAME, 'w') as csvfile:
    w = csv.writer(csvfile)
    for r in first_rows:
        w.writerow(r)

    year_number = 1
    total_ecs = 0

    for year in sorted(academic_years):
        title = '%s year %d:' % (LEVEL, year_number)
        w.writerow([])
        w.writerow([title])
        w.writerow(HEADER_ROW)
        courses = sorted(academic_years[year], key=lambda x: x[COURSE_NAME])
        for i in range(len(courses)):
            c = courses[i]
            row = [i + 1, c[COURSE_NAME], c[COURSE_CODE], c[CREDITS], c[GRADE_DATE]]
            if c[COURSE_CODE] in MINORS:
                row.append('MINOR')
            w.writerow(row)

        ecs_this_year = sum([int(c[CREDITS]) for c in courses])
        w.writerow(['', '', 'Total EC year %d' % year_number, ecs_this_year])

        year_number += 1
        total_ecs += ecs_this_year

    w.writerow([])

    w.writerow(['Name Minor:', MINOR_NAME])
    w.writerow(['University that facilitates the minor:', MINOR_UNI_NAME])

    w.writerow([])

    w.writerow(['On behalf of the Examination Board'])
    w.writerow(['Name:', '', 'Date:'])
    w.writerow([])
    w.writerow([])
    w.writerow(['Signature:'])

print("Created your 'Academic Profile' CSV form")
pyplot.scatter(times, grades)
savefig('grades.png')
print('Saved a scatterplot of your grades over time to grades.png')
print('Average grade: %0.2f' % (sum(grades) / len(grades)))
print('Current ECTS: %d' % (total_ecs - sum([i[CREDITS] for i in FUTURE])))
print('ECTS after passing planned modules: %d' % total_ecs)
