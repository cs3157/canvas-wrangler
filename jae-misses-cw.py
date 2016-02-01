import sys
import csv
import requests

if len(sys.argv) < 3:
	print 'usage:', sys.argv[0], '<csv>', '<assignment_id>', '[<sdb>]'
	exit()

if len(sys.argv) == 3:
	print 'Using default sdb.csv path'
	sdbPath = 'sdb.csv'
else:
	sdbPath = sys.argv[3]

# set assignment id
apiUrl = 'https://courseworks2.columbia.edu/api/v1/courses/6858/assignments/'+sys.argv[2]+'/submissions/update_grades'

# set authorization header for POST request
# replace with your own authentication key
authHeader = {'Authorization': 'Bearer <your-auth-key>'}

# John authHeader
# authHeader = {'Authorization': 'Bearer 1396~1AFU0JIBRRj26TY4QIfR8bLbtwvwg05yx3dDWMtzfBXrFgZi0N9B29r2s2k4mWOY'}



# populate student UNI->user_id lookup dict from sdb.csv
sLookup = {}
sdb = csv.reader(open(sdbPath, 'r'))
for s in sdb:
	sLookup[s[0]] = s[1]

# open and read lab grades csv
grades = csv.reader(open(sys.argv[1], 'r'))
grades.next() # skip header

# formatted 
uniCol = 2
gradeCol = 3
commentCol = 4

# populate POST request data
postData = {}
for r in grades:
	if r[uniCol] in sLookup:
		user = 'grade_data[' + sLookup[r[uniCol]] + ']'
		postData[user + '[posted_grade]'] = r[gradeCol]
		postData[user + '[text_comment]'] = r[commentCol]
	else:
		print 'Warning:', r[uniCol], 'not found in sdb'

# check comment for fdp2107
# print postData['grade_data[' + sLookup['fdp2107'] + ']' + '[text_comment]']

# test with TestStudent
# postData['grade_data[273328][text_comment]']' = 'Nice UNI'
# postData['grade_data[273328][posted_grade]'] = '42'

# print datas
# ^very ugly

# post request and print response
# print requests.post(apiUrl, data=datas, headers=authHeader).json()