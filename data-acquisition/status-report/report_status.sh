#!/bin/bash

echo 'Good Morning Aman.' >> ~/status/status.txt
#echo 'Good Morning Aman, Jack, Nichole.' >> ~/status/status.txt
echo "" >> ~/status/status.txt

echo 'We have come out of hibernation to schedule a new day of observations.' >> ~/status/status.txt
echo 'A brief status report on Project "Spy On the Spy Satellites".' >> ~/status/status.txt
echo "" >> ~/status/status.txt
echo "" >> ~/status/status.txt

cat ~/status/ref.txt >> ~/status/status.txt
cat ~/status/t1a.txt >> ~/status/status.txt
cat ~/status/t1b.txt >> ~/status/status.txt
cat ~/status/t2.txt >> ~/status/status.txt
cat ~/status/t2b.txt >> ~/status/status.txt


echo 'Until Tomorrow,' >> ~/status/status.txt
echo 'Council of Pis' >> ~/status/status.txt

python mwa_mail.py

rm ~/status/*.txt
