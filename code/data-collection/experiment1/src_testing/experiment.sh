#!/bin/sh

echo "${#1}" "${#2}"
path="`dirname \"$0\"`"
echo $path
masterpath=$(pwd)

if (( ${#1} < 1 )) || (( ${#2} < 1 ));
then
echo "Missing -s or ex/tb"
exit 1
fi

if [ "${1}" != "-s" ] || [ "${2}" != "ex" ] && [ "${2}" != "tb" ];
then
echo "Wrong inputs"
exit 1
fi

# echo '\nStarting script to check thermal image...\n'
# python ${path}/thermal_camera_check.py $1 $2
# echo '\nScript to check thermal image done...\n'

# echo '\nStarting script to check set of Zaber\n'
# python ${path}/zabers_check.py $1 $2
# echo '\nScript to check set of Zabers is done...\n'

echo '\nStarting script to find the right height for zabers\n'
python ${path}/height_finding.py $1 $2
echo '\nScript to find the right height is done...\n'

echo '\nStarting script to find the ROI per grid position\n'
python ${path}/grid_roi_finding.py $1 $2
echo '\nScript for finding the ROI per grid position is done...\n'

echo '\nStarting script to train on task...\n'
python ${path}/training.py $1 $2
echo '\nScript for training on task is done...\n'

echo '\nStarting script to perform STAIRCASE on the grid...\n'
python ${path}/exp_stair.py $1 $2
echo '\n\nScript for STAIRCASE is done...\n\n'

echo '\nStarting script to calculate DELTA target...\n'
python ${path}/delta_calc.py $1 $2
echo '\n\nScript for calculating DELTA TARGET is done...\n\n'

echo '\nStarting script to perform SDT on the grid...\n'
python ${path}/exp_sdt.py $1 $2
echo '\n\nThe experiment is done!\n\n'

echo '\n\nSending data to computer office...\n\n'

folder_name=$(cat $path/temp_folder_name.txt)
username=$(cat $path/username)

server_name=$(cat /Users/$username/.ssh/server_name_icn)
cip=$(cat /Users/$username/.ssh/server_hostname_icn)

scp -rv "$masterpath/data/$folder_name" $server_name@$cip:/home/ivan/Documents/phd/coding/python/phd/experiment1/data

echo '\n\nData in computer office..\n\n'

echo '\n\nStart analysis script..\n\n'

echo $folder_name
echo $server_name
echo $cip

nohup ssh $server_name@$cip "cd /home/ivan/Documents/phd/coding/python/phd/experiment1/data && /home/ivan/Documents/phd/coding/python/phd/experiment1/src_analysis/automatic/auto_anal.sh $folder_name" &

echo '\n\nAnalysis is done!\n\n'

rm $path/temp_folder_name.txt