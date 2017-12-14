# VU Academic Profile maker

VU Amsterdam requires students to fill in a spreadsheet containing with their list of completed courses, 
along with their course codes, number of ECTS credits, and date of grade received. 
Not sure why, since all this data is already in VU's system. 

This script saves you some labor by taking a html file you download from within VUNet as input, and extracts the relevant information from it.
It then constructs a CSV file (almost) matching the template provided by VU. 

To use, first log in to VUnet, then visit [this vunet page](https://vunet.login.vu.nl/Pages/SelfServices/Study/moduleoverview.aspx)
and expand all the result tables. Then save the web page (CTRL+S) and do `python3 make_vu_academic_profile.py path/to/moduleoverview.aspx`