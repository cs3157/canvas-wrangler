Canvas Wrangler
===============
> Dear CourseWorks,
> 
> I am so so sorry that I made fun of you and called you names.  
> I called you CourseSucks all the time.  
> I take it back.  
> 
> You are air.  
> You are water.  
> I never thought about what would happen to me if you left.  
> I am going to cling to you as long as I can.  
> I love you.
> 
> Jae

Authentication Key Creation
---------------------------
In order to interface with the Canvas API, one must generate an authentication token from Canvas. This can be done in the Settings Panel, in the Approved Integrations section. Click "New Access Token", specify a legitimate purpose, and optionally an expiration date. The next dialogue will display a generated string that will act as your authentication token.

_Be sure to save the authentication token somewhere safe! Apparently it can't be recovered from Canvas once the dialogue is closed._

Export your OAuth token as an environmental variable named `CANVASPONIES`

Student Database Creation
-------------------------
On Canvas, each student has a unique, numeric user id. These are needed in order to translate each student's UNI to their user id. 

These are maintained in a student database file (named sdb.csv by default)

The student database is created using the Grades spreadsheet from Canvas. To create/update the spreadsheet, run the command:

    python sdbMake.py <input: grades csv spreadsheet> [<output: student csv database>]

_If the optional student database filename is not specified, the default of sdb.csv will be used_

The format for each row of the sdb.csv is `<UNI>,<user id>`

Grade Spreadsheet Format
------------------------
The grade spreadsheet should be a .csv file. Each column for each student in the grade spreadsheet should be in the following format:
    <TA#>,<TA>,<uni>,<grade>,<comment>

There should be a single header row that contains the names of each column. It should be exactly as follows: `TA#,TA,uni,grade,comment`, as the default indices are hardcoded into the program. If the header row is blank or malformed, this is the format that will be assumed.

However, if the order is shuffled or there are extra columns, as long as the keywords `uni`, `grade`, and `comment` are present, the program will override and correct its default indices.

Grade and Comment Submission
----------------------------
In order to batch upload both comments and grades, this program uses the Canvas API's update\_grades endpoint.

The program uses sdb.csv as a UNI lookup table, to translate from a student's UNI to their user id.

The program requires the course id; this is the last portion of the course page's URL. For example, in [https://courseworks2.columbia.edu/courses/6858](https://courseworks2.columbia.edu/courses/6858) the course id is 6858.

The program also requires the assignment id for each lab; this is the last portion of the assignment page's URL. For example, in [https://courseworks2.columbia.edu/courses/6858/assignments/25314](https://courseworks2.columbia.edu/courses/6858/assignments/25314) the assignment id is 25314.

The program updates each student's grade record by reading the from the lab grades csv spreadsheet and creating a new form entry for each comment and grade with their user id. This should work even if the student has not submitted any files for the assignment.

To upload grades, run the command:

    python canvas-wrangler.py <course id> <assignment id> <grades spreadsheet> [<sdb>]

_Specifying the sdb.csv path is optional; if it is missing, the program will try to open ./sdb.csv by default._

Other Remarks
-------------
If there are any problems/suggestions, please feel free to contact me about them at [j.hui@columbia.edu](mailto:j.hui@columbia.edu)
