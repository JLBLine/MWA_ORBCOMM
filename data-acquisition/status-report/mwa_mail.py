import os
import pytz
import smtplib
import datetime



user_id = 'mwa.beam@gmail.com'
gmail_password = '##############'
#to = ['achokshi@student.unimelb.edu.au', 'nichole.barry@unimelb.edu.au', 'jack.line@curtin.edu.au']
to = ['achokshi@student.unimelb.edu.au']

date = datetime.datetime.now(pytz.timezone('Australia/Perth')).strftime("%Y-%m-%d-%H:%M")

os.chdir(r"/home/amanchokshi/status")

with open("status.txt") as f:
    txt = f.read()


subject = 'MWA Beam Experiment Status - [%s]' %(date)
body = txt

msg = """Subject: %s

%s
""" % (subject, body)

s = smtplib.SMTP('smtp.gmail.com', 587)
s.ehlo()
s.starttls()
s.ehlo()
s.login(user_id, gmail_password) 

s.sendmail(user_id, to, msg) 

s.quit() 
