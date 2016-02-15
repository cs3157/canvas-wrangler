import os
import argparse
import csv
import requests

# parser object
parser = argparse.ArgumentParser(description='Upload grades and comments to Canvas')

# grade options
parser.add_argument('-g', '--grade',
                    default=False, action='store_true',
                    help='upload grades')
parser.add_argument('-G', '--grade-col',
                    default='grade', type=str,
                    help='set name for grade header column',
                    metavar='<header>')

# comment options
parser.add_argument('-c', '--comment',
                    default=False, action='store_true',
                    help='upload comments')
parser.add_argument('-C', '--comment-col',
                    default='comment', type=str,
                    help='set name for comment header column',
                    metavar='<header>')

# student options
parser.add_argument('-s', '--sdb',
                    default='sdb.csv', type=argparse.FileType('r'),
                    help='csv spreadsheet containing each student\'s user-id',
                    metavar='<sdb.csv>')
parser.add_argument('-S', '--student-col',
                    default='uni', type=str,
                    help='set name for student header column',
                    metavar='<header>')

# required positional args
parser.add_argument('course_id',
                    type=int,
                    help='course-id from Canvas',
                    metavar='<course-id>')
parser.add_argument('assignment_id',
                    type=int,
                    help='assignment-id from Canvas',
                    metavar='<assignment-id>')
parser.add_argument('grades',
                    type=argparse.FileType('r'),
                    help='csv spreadsheet containing grades and/or comments',
                    metavar='<grades.csv>')

# parse args into args
args = parser.parse_args()

# set assignment id
apiUrl = 'https://courseworks2.columbia.edu/api/v1' \
        +'/courses/'+args.course_id \
        +'/assignments/'+args.assignment_id \
        +'/submissions/update_grades'

# open csv files
grades = csv.reader(args.grades)
sdb = csv.reader(args.students)

# determine whether or not to submit grades or comments or both
submit_grade = args.grade
submit_comment = args.comment
if not (submit_grade or submit_comment):
    submit_grade = submit_comment = True

# set authorization header for POST request
# replace with your own authentication key
authVar = 'CANVASPONIES'
if not os.environ.has_key(authVar):
    print 'Error: authentication token enviromental variable', authVar, 'not set.'
    exit(-1)
authHeader = {'Authorization': 'Bearer ' + os.environ[authVar]}

# populate student UNI->user id lookup dict from sdb.csv
students = {}
for s in sdb:
    students[s[0]] = s[1]

header_col = grades.next()
for i in range(len(header_col)):
    if header_col[i].lower() == args.uni_col:
        uni_col = i
        break
if not uni_col:
    print 'Error: could not find UNI header', args.uni_col
    exit()

if submit_grade:
    for i in range(len(header_col)):
        if header_col[i].lower() == args.grade_col:
            grade_col = i
            break
    if not grade_col:
        print 'Error: could not find grade column header', args.grade_col
        exit()

if submit_comment:
    for i in range(len(header_col)):
        if header_col[i].lower() == args.comment_col:
            comment_col = i
            break
    if not comment_col:
        print 'Error: could not find comment column header', args.comment_col
        exit()

postData = {}
# populate POST request data
for r in grades:
    if r[uni_col] in students:
        user = 'grade_data[' + students[r[uni_col]] + ']'
        if submit_grade:
            postData[user + '[posted_grade]'] = r[grade_col]
        if submit_comment:
            postData[user + '[text_comment]'] = r[comment_col]
    else:
        print 'Warning:', r[uni_col], 'not found in sdb'

# post request and print response
print requests.post(apiUrl, data=postData, headers=authHeader).json()
