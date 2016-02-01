import sys
import csv
import requests
import os

if len(sys.argv) < 3:
	print 'usage:', sys.argv[0], '<course id>', '<assignment id>', '<grades spreadsheet>' ' [<sdb>]'
	exit()

courseId = sys.argv[1]
assignmentId = sys.argv[2]
gradesPath = sys.argv[3]

if len(sys.argv) == 4:
	print 'Using default sdb path: sdb.csv'
	sdbPath = './sdb.csv'
else:
	sdbPath = sys.argv[4]

# set assignment id
apiUrl = 'https://courseworks2.columbia.edu/api/v1/courses/'+courseId+'/assignments/'+assignmentId+'/submissions/update_grades'

# set authorization header for POST request
# replace with your own authentication key
authVar = 'CANVASPONIES'
if os.environ.has_key(authVar):
	print 'Error: authentication token enviromental variable', authVar, 'not set.'
	exit()

authHeader = {'Authorization': 'Bearer ' + os.environ[authVar]}

# populate student UNI->user id lookup dict from sdb.csv
sLookup = {}
sdb = csv.reader(open(sdbPath, 'r'))
for s in sdb:
	sLookup[s[0]] = s[1]

# open and read lab grades csv
grades = csv.reader(open(gradesPath, 'r'))

# default format
uniCol, gradeCol, commentCol = 2, 3, 4 # default indices
uniT = gradeT = commentT = -1

# calibrate column indices
headerCol = grades.next()
for i in range(0,len(headerCol)):
	if headerCol[i].lower() == 'uni':
		uniT = i
	elif headerCol[i].lower() == 'grade':
		gradeT = i
	elif headerCol[i].lower() == 'comment':
		commentT = i
if uniT == -1 or gradeT == -1 or commentT == -1:
	print 'Error: badly formatted header row'
	exit()
# set column indices
uniCol, gradeCol, commentCol = uniT, gradeT, commentT

postData = {}
# populate POST request data
for r in grades:
	if r[uniCol] in sLookup:
		user = 'grade_data[' + sLookup[r[uniCol]] + ']'
		postData[user + '[posted_grade]'] = r[gradeCol]
		postData[user + '[text_comment]'] = r[commentCol]
	else:
		print 'Warning:', r[uniCol], 'not found in sdb'

# post request and print response
print requests.post(apiUrl, data=postData, headers=authHeader).json()
