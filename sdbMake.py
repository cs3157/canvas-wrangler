#!/usr/bin/env python2
import sys
import csv

if len(sys.argv) < 2:
    print "usage:", sys.argv[0], "<input: grades csv spreadsheet>", " [<output: student csv database>]"
    exit()

inPath = sys.argv[1]
if len(sys.argv) < 3:
    print 'Using default output filename: sdb.csv'
    outPath = 'sdb.csv'
else:
    outPath = sys.argv[2]

# column indices in grades spreadsheet
userIdCol = 1
uniCol = 2

# initialise student database
sdb = {}

# open grades spreadsheet for reading
grades = csv.reader(open(inPath, 'r'))

# skip over headers
grades.next()
grades.next()

# read grades into student database
for r in grades:
    sdb[r[uniCol]] = r[userIdCol]

# write out student database
sdbWriter = csv.writer(open(outPath, 'w'))

for k, v in sdb.items():
    sdbWriter.writerow([k, v])
