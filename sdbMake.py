import sys
import csv


if len(sys.argv) < 3:
	print "usage:", sys.argv[0], "<csv>", "<sdb>"
	exit()

uniCol = 2
userIdCol = 1

sdb = {}

csvReader = csv.reader(open(sys.argv[1], 'r'))

csvReader.next()
csvReader.next()

for r in csvReader:
	sdb[r[uniCol]] = r[userIdCol]

sdbWriter = csv.writer(open(sys.argv[2], 'w'))

for k, v in sdb.items():
	sdbWriter.writerow([k, v])