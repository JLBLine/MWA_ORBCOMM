# This needs to run at 5:30AM everyday.

# Creates and begins populating the status.txt file, which will be the body of the email.
echo "touch /home/jline/t2b.txt" | at 05:40
echo "echo \"# TILES2B PI #\" >> /home/jline/t2b.txt" |at 05:41
echo "echo \" \" >> /home/jline/t2b.txt" |at 05:42
echo "echo \"[05:30AM]: Sourced one_script_to_rule_them_all.sh \" >> /home/jline/t2b.txt" |at 05:43
# Creates a queue of at jobs from 6AM-6AM.
# Adds  line to status.txt, confirming that jobs for the next day are in the queue.
at 05:45 < make_night_schedule.sh 

# At 6:05AM, check to see if there are 24*2*4 files in ./data/*/*.
# If there are, source do_rsync.sh then source clear_data.sh. Send email to Aman.
# If there are files missing, source do_rsync, but don't clear data. Send email to Aman, Jack, Nichole.
# Emails are sent at 6:20AM

echo "echo \"[06:00AM]: A new day of spying on satellites begins \" >> /home/jline/t2b.txt" |at 05:55
echo "echo \"[06:02AM]: Checking for missing data files from the last 24 hours.\" >> /home/jline/t2b.txt" | at 06:02
at 06:03 < /home/jline/check_missing.sh
at 06:04 < /home/jline/do_rsync_clear.sh

echo "scp /home/jline/t2b.txt cerberus:/home/amanchokshi/status" | at 06:23

# Clean up and get ready for next day
echo "rm /home/jline/t2b.txt" | at 06:25
