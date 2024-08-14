#!/bin/bash
# exec 1>/home/ivan/log-output.txt 2>/home/ivan/log-errors.txt

printf '\n\nAuto analysis script triggered in server...\n\n'
exptfolder='experiment1'

touch /home/ivan/Documents/phd/coding/python/phd/$exptfolder/src_analysis/automatic/temp_folder_analyse
export PYTHONPATH="${PYTHONPATH}:/home/ivan/Documents/phd/coding/python/phd/classes"

name_file=$1
# name_file=$(sed -e 's/^"//' -e 's/"$//' <<<"$name_file")
echo $name_file > /home/ivan/Documents/phd/coding/python/phd/experiment1/src_analysis/automatic/temp_folder_analyse
echo $name_file

printf '\n\nSTARTING DIRTY blind responses analysis\n\n'
/home/ivan/.pyenv/shims/python /home/ivan/Documents/phd/coding/python/phd/$exptfolder/src_analysis/automatic/auto_blind_responses_check.py -f $name_file
printf '\n\nBlind DIRTY responses analysis DONE!\n\n'

printf '\n\nSTARTING CLEAN BLIND responses analysis\n\n'
/home/ivan/.pyenv/shims/python /home/ivan/Documents/phd/coding/python/phd/$exptfolder/src_analysis/automatic/auto_clean_blind_responses_check.py -f $name_file
printf '\n\nBlind CLEAN BLIND responses analysis DONE\n\n'

printf '\n\nSTARTING PDF BUILDER\n\n'
/home/ivan/.pyenv/shims/python /home/ivan/Documents/phd/coding/python/phd/$exptfolder/src_analysis/automatic/auto_pdf_graphs.py -f $name_file
printf '\n\nPDF BUILDER DONE\n\n'

printf '\n\nSTARTING automatic STAIRCASE analysis\n\n'
/home/ivan/.pyenv/shims/python /home/ivan/Documents/phd/coding/python/phd/$exptfolder/src_analysis/automatic/auto_ani_staircase.py -f $name_file
printf '\n\nAutomatic STAIRCASE analysis DONE\n\n'

printf '\n\nSTARTING automatic SDT analysis\n\n'
/home/ivan/.pyenv/shims/python /home/ivan/Documents/phd/coding/python/phd/$exptfolder/src_analysis/automatic/auto_ani_sdt.py -f $name_file
printf '\n\nAutomatic MoL analysis DONE\n\n'

rm /home/ivan/Documents/phd/coding/python/phd/$exptfolder/src_analysis/automatic/temp_folder_analyse