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

# warning log options
parser.add_argument('-L', '--log',
                    default='', type=str,
                    help='set filename for warning log',
                    metavar='<warning.log>')
parser.add_argument('-N', '--no-log',
                    default=False, action='store_true',
                    help='do not produce log file for warnings')

# testing options
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
grades_name = args.grades.name
grades = csv.reader(args.grades)
sdb_name = args.sdb.name
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

# determine warning log name
if len(args.log) == 0:
    log_name = grades_name.rsplit('.', 1)[0] + '-warning.log'
else:
    log_name = args.log

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
missing_err = []
comment_err = []
grade_err = []

# populate POST request data
for i, r in enumerate(grades):
    if r[uni_col] in students:
        user = 'grade_data[' + students[r[uni_col]] + ']'
        if submit_grade:
            try:
                float(r[grade_col])
                post_data[user + '[posted_grade]'] = r[grade_col]
            except ValueError:
                grade_err.append((i+2, r[uni_col], r[grade_col]))
                print 'Warning: grade is not numeric'
                print '{0}:{1}: {2} '.format(grades_name, i+2, r[grade_col])
                print 'Not sumbitting grade for', r[uni_col]
                print
        if submit_comment:
            try:
                r[comment_col].decode('utf-8')
                post_data[user + '[text_comment]'] = r[comment_col]
            except UnicodeDecodeError:
                comment_err.append((i+2, r[uni_col], r[comment_col]))
                print 'Warning: comment contains invalid characters'
                print '{0}:{1}: {2} '.format(grades_name, i+2, r[comment_col])
                print 'Not submitting comment for', r[uni_col]
                print
    else:
        missing_err.append((i+2, r[uni_col], r[grade_col], r[comment_col]))
        print 'Warning:', r[uni_col], 'not found in sdb'
        print

########################
##### Log Warnings #####
########################

merrlen, gerrlen, cerrlen = len(missing_err), len(grade_err), len(comment_err)

if not args.no_log:
    if (merrlen > 0 or gerrlen > 0 or cerrlen > 0):
        err_report = '{0} missing UNIs, {1} non-numeric grades, and {2} invalid comments.\n'.format(merrlen, gerrlen, cerrlen)

        log = open(log_name, 'w')
        log.write('=========================================================\n')
        log.write('====================== Error Log ========================\n')
        log.write('=========================================================\n')
        log.write('Gradesheet filename: {0}\n'.format(grades_name)) 
        log.write('Student database filename: {0}\n'.format(sdb_name)) 
       
        log.write(err_report)
        if merrlen > 0:
            log.write('\n== Missing UNIs ==')
            log.write('\n------------------\n')
            for err in missing_err:
                log.write('{0}:{1}:'.format(err[0], err[1]))
                log.write('\n\tgrade:{0}\n\tcomment:{1}\n'.format(err[2],err[3]))
        if gerrlen > 0:
            log.write('\n== Non-numeric Grades ==')
            log.write('\n------------------------\n')
            for err in grade_err:
                log.write('{0}:{1}: {2}\n'.format(err[0], err[1], err[2]))
        if cerrlen > 0:
            log.write('\n== Invalid Comments ==')
            log.write('\n----------------------\n')
            for err in comment_err:
                log.write('{0}:{1}: {2}\n'.format(err[0], err[1], err[2]))
        log.close()
        print err_report
    else:
        print 'No warnings generated; no warning log created.\n'
else:
    print '--no-log: Not creating warning log.\n'

#################################
##### Submission and Report #####
#################################

if args.no_submit:
    print ' --no-submit option specified; not submitting to Canvas.'
    print '========================================================='
    print '==================== Program Report ====================='
    print '========================================================='
    print
    print '== args =='
    print '----------'
    pprint.pprint(vars(args))
    print
    print '== post_data =='
    print '---------------'
    pprint.pprint(post_data)
    print
    print '========================================================='
    print
    exit(0)

# post request and print response
try:
    res = requests.post(URL, data=post_data, headers=HEADER)
    res_code = res.status_code
    res = res.json()
except requests.exceptions.ConnectionError:
    print 'Error: internet connection error'
    print 'Could not submit grades and comments'
    print
    exit(-1)

if res_code == requests.codes.ok:
    # success
    print 'Grades and comments successfully submitted!'
    print '========================================================='
    print '================== Submission Report ===================='
    print '========================================================='
    print 'Course ID:', res['context_id']
    print 'Assignment ID:', res['id']
    print
    print 'Please wait as Canvas processes this POST request...'
    print 'Feel free to check its progress at:'
    print res['url']
    print '========================================================='
    print
    exit(0)
else:
    print 'Error:', res_code
    print '========================================================='
    print '===================== Error Report ======================'
    print '========================================================='
    print 'Error report ID:', res['error_report_id']
    for error in res['errors']:
        print 'Error message:', error['message']
        print 'Error code:', error['error_code']
    print
    print 'If that wasn\'t helpful (which it usually isn\'t),'
    print 'please try the following:'
    print '\t* Make sure assignment is published'
    print '\t* Remove potential bad unicode characters'
    print '\t\t(most commonly smart quotation marks)'
    print '\t* Try again later; might actually be a server error?'
    print '\t* Try turning your computer off and on again'
    print '\t  ^^^ please don\'t actually'
    print
    print 'Also please contact j.hui@columbia.edu about this error'
    print '========================================================='
    print
    exit(res_code)
