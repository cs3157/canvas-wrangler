#!/usr/bin/python
import os
import argparse
import csv
import requests
import pprint

#################################
##### Parser Configurations #####
#################################

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
                    default='sdb.csv', type=argparse.FileType('rU'),
                    help='csv spreadsheet containing each student\'s user-id',
                    metavar='<sdb.csv>')
parser.add_argument('-S', '--student-col',
                    default='uni', type=str,
                    help='set name for student header column',
                    metavar='<header>')

# required positional args
parser.add_argument('course_id',
                    type=str,
                    help='course-id from Canvas',
                    metavar='<course-id>')
parser.add_argument('assignment_id',
                    type=str,
                    help='assignment-id from Canvas',
                    metavar='<assignment-id>')
parser.add_argument('grades',
                    type=argparse.FileType('rU'),
                    help='csv spreadsheet containing grades and/or comments',
                    metavar='<grades.csv>')

parser.add_argument('-n', '--no-submit',
                    default=False, action='store_true',
                    help='do not submit grades; for testing purposes')

###########################################
##### Parse Args and Preliminary Work #####
###########################################

# parse args into args
args = parser.parse_args()

# set assignment id
URL = 'https://courseworks2.columbia.edu/api/v1' \
        +'/courses/'+args.course_id \
        +'/assignments/'+args.assignment_id \
        +'/submissions/update_grades'

# open csv files
grades = csv.reader(args.grades)
sdb = csv.reader(args.sdb)

# determine whether or not to submit grades or comments or both
submit_grade = args.grade
submit_comment = args.comment
if not (submit_grade or submit_comment):
    submit_grade = submit_comment = True

# set authorization header for POST request
# replace with your own authentication key
AUTHVAR = 'CANVASPONIES'
if not os.environ.has_key(AUTHVAR):
    print 'Error: authentication token enviromental variable', AUTHVAR, 'not set.'
    exit(1)
HEADER = {'Authorization': 'Bearer ' + os.environ[AUTHVAR]}


####################################
##### Calibrate Column Indices #####
####################################

# populate student UNI->user id lookup dict from sdb.csv
students = {}
for s in sdb:
    students[s[0]] = s[1]

header_col = grades.next()
for i in range(len(header_col)):
    if header_col[i].lower() == args.student_col:
        uni_col = i
        break
try:
    uni_col
except NameError:
    print 'Error: could not find UNI header:', args.uni_col
    exit(2)

if submit_grade:
    for i in range(len(header_col)):
        if header_col[i].lower() == args.grade_col:
            grade_col = i
            break
    try:
        grade_col
    except NameError:
        print 'Error: could not find grade column header:', args.grade_col
        exit(3)

if submit_comment:
    for i in range(len(header_col)):
        if header_col[i].lower() == args.comment_col:
            comment_col = i
            break
    try:
        comment_col
    except NameError:
        print 'Error: could not find comment column header:', args.comment_col
        exit(4)


########################
##### Prepare Data #####
########################

post_data = {}
# populate POST request data
for r in grades:
    if r[uni_col] in students:
        user = 'grade_data[' + students[r[uni_col]] + ']'
        if submit_grade:
            try:
                float(r[grade_col])
                post_data[user + '[posted_grade]'] = r[grade_col]
            except ValueError:
                print 'Warning:', r[grade_col], 'is not numeric'
                print 'Not sumbitting grade for', r[uni_col]
        if submit_comment:
            try:
                r[comment_col].decode('utf-8')
                post_data[user + '[text_comment]'] = r[comment_col]
            except UnicodeDecodeError:
                print 'Warning:', r[comment_col], 'contains bad characters'
                print 'Not submitting comment for', r[uni_col]
    else:
        print 'Warning:', r[uni_col], 'not found in sdb'

#################################
##### Submission and Report #####
#################################

if args.no_submit:
    print 
    print ' --no-submit option specified; not submitting to Canvas.'
    print '========================================================='
    print '==================== Program Report ====================='
    print '========================================================='
    print
    print '/****** args ******/'
    pprint.pprint(vars(args))
    print
    print '/*** post_data ***/'
    pprint.pprint(post_data)
    print
    print '========================================================='
    print
    exit(0)

# post request and print response
res = requests.post(URL, data=post_data, headers=HEADER)
res_code = res.status_code
res = res.json()

print
if res_code == requests.codes.ok:
    # success
    print 'Grades and comments successfully submitted!'
    print '========================================================='
    print '================== Submission Report ===================='
    print '========================================================='
    print 'Course ID:', res['context_id']
    print 'Assignment ID:', res['id']
    print
    print 'Please wait as Canvas processes the POST request...'
    print 'Feel free to check its progress at:'
    print res['url']
    exit(0)
else:
    print 'Error:', res_code
    print '========================================================='
    print '===================== Error Report ======================'
    print '========================================================='
    print
    print 'Error report ID:', res['error_report_id']
    for error in res['errors']:
        print 'Error message:', error['message']
        print 'Error code:', error['error_code']
    print
    print 'If that wasn\'t helpful (which it usually isn\'t)'
    print 'please try the following:'
    print '\t*Make sure assignment is published'
    print '\t*Remove potential bad unicode characters'
    print '\t\t(most commonly smart quotation marks)'
    print '\t*Try again later; might actually be a server error?'
    print '\t*Try turning your computer off and on again'
    print '\t ^^^ please don\'t actually'
    print
    print 'Also please contact j.hui@columbia.edu about this error'
    exit(res_code)
