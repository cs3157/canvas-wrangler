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

Export your OAuth token as an environmental variable named `CANVASPONIES` in your command line shell.

Student Database Creation
-------------------------
On Canvas, each student has a unique, numeric user id. These are needed in order to translate each student's UNI to their user id. 

These are maintained in a student database file (named sdb.csv by default)

The student database is created using the Grades spreadsheet from Canvas. To create/update the spreadsheet, run the command:

    python sdbMake.py <input: grades csv spreadsheet> [<output: student csv database>]

_If the optional student database filename is not specified, the default of sdb.csv will be used_

The format for each row of the sdb.csv is `<UNI>,<user-id>`

Grade Spreadsheet Format
------------------------
The grade spreadsheet should be a .csv file. Entries containing commas should be wrapped in quotation marks (e.g. `"contains a comma, this entry"`), and quotation marks should be 'escaped' using double quotation marks (e.g. `"this entry ""uses"" quotation marks"`). (Exporting a .csv from Google Docs will do this for you.)

The grade spreadsheet must contain a single header row so that Canvas Wrangler can calibrate its column indices. By default, Canvas Wrangler will expect the grade column to be named `grade` and the comment column to be named `comment`. However, these can be overridden by using the `-G` and `-C` flags respectfully and specifying the header name after the flag argument (e.g. `python canvas-wrangler.py -G studentgrade`).

Grade and Comment Submission
----------------------------
In order to batch upload both comments and grades, this program uses the Canvas API's update\_grades endpoint. By default, Canvas Wrangler will try to upload both grades and comments. However, if either the `-c` or the `-g` are specified, Canvas Wrangler will only upload what has been specified by flag options.

By default, Canvas Wrangler will try to open `sdb.csv` and use it as the UNI lookup table, to translate from a student's UNI to their user id. The filename can be overridden using the `-s` flag, but it should always be the same format.

The program requires the course id; this is the last portion of the course page's URL. For example, in [https://courseworks2.columbia.edu/courses/6858](https://courseworks2.columbia.edu/courses/6858) the course id is 6858.

The program also requires the assignment id for each lab; this is the last portion of the assignment page's URL. For example, in [https://courseworks2.columbia.edu/courses/6858/assignments/25314](https://courseworks2.columbia.edu/courses/6858/assignments/25314) the assignment id is 25314.

The program updates each student's grade record by reading the from the lab grades csv spreadsheet and creating a new form entry for each comment and grade with their user id. This should work even if the student has not submitted any files for the assignment.

To upload grades, run the command:

    python canvas-wrangler.py <course id> <assignment id> <grades spreadsheet>

_The assignment must be puslished before grades and comments can be uploaded._

To run Canvas Wrangler without submitting to Canvas, for testing, use the `-n` flag. The program will print out information about the arguments and the data it was going to post, then quit before submitting to Canvas.

For additional information about usage of flags, run `python canvas-wrangler.py --help`

Other Remarks
-------------
If you have any problems/suggestions/complaints/_love letters to the old Courseworks_, please feel free to contact me about them at [j.hui@columbia.edu](mailto:j.hui@columbia.edu)
