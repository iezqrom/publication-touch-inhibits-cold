#!/bin/sh
echo "${#1}" "${#2}"
path="`dirname \"$0\"`"
echo $path
masterpath=$(pwd)

username=$(cat $path/username)

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

read -t 1 -n 10000 discard
clear
name_scripts=('Thermal camera check' 'Zabers check' 'Touch stability' 'Height finding' 'Extrapolation of heights' 'Grid ROI finding' 'Training Staircase' 'Staircase' 'Delta calculation' 'SDT replication' 'Analyse behavioural data' 'Analyse thermal videos')
PS3='What Python script would you like to start with?   '
read -t 1 -n 10000 discard
select opt in "${name_scripts[@]}"; do
for i in "${!name_scripts[@]}"; do
    if [[ "${name_scripts[$i]}" = "${opt}" ]]; then
        index_start="${i}";
    fi
    done
    break
done

clear
if (( $index_start < 1 )); then
    echo '\nStarting script to check thermal image...\n'
    python ${path}/thermal_camera_check.py $1 $2
    echo '\nScript to check thermal image DONE...\n'
fi

clear
if (( $index_start < 2 )); then
    echo '\nStarting script to check set of Zaber\n'
    python ${path}/zabers_check.py $1 $2
    echo '\nScript to check set of Zabers is DONE...\n'
fi

clear
if (( $index_start < 3 )); then
    echo '\nStarting script to check set of Zaber\n'
    python ${path}/touch_stability.py $1 $2
    echo '\nScript to check set of Zabers is DONE...\n'
fi

clear
if (( $index_start < 4 )); then
    echo '\nStarting script to find master grid point\n'
    python ${path}/master_height_finding.py $1 $2
    echo '\nScript to find master grid point DONE...\n'
fi

clear
if (( $index_start < 5 )); then
    echo '\nStarting script to find master grid point\n'
    python ${path}/height_extrapolation.py $1 $2 $3 $4
    echo '\nScript to find master grid point DONE...\n'
fi

clear
if (( $index_start < 6 )); then
    echo '\nStarting script to find the ROI per grid position\n'
    python ${path}/grid_roi_finding.py $1 $2 $3 $4
    echo '\nScript for finding the ROI per grid position is DONE...\n'
fi

clear
if (( $index_start < 7 )); then
    echo '\nStarting script to train on task...\n'
    python ${path}/training.py $1 $2 $3 $4
    echo '\nScript for training on task is DONE...\n'
fi

clear
if (( $index_start < 8 )); then
    echo '\nStarting script to perform STAIRCASE on the grid...\n'
    python ${path}/exp_stair.py $1 $2 $3 $4
    echo '\n\nScript for STAIRCASE is DONE...\n\n'
fi

clear
if (( $index_start < 9 )); then
    echo '\nStarting script to calculate DELTA...\n'
    python ${path}/delta_calc.py $1 $2 $3 $4
    echo '\n\nScript for DELTA calculation is DONE...\n\n'
fi

clear
if (( $index_start < 10 )); then
    echo '\nStarting script to perform SDT on the grid...\n'
    python ${path}/exp_sdt_control.py $1 $2 $3 $4
    echo '\n\nScript for SCALING is DONE...\n\n'
fi

clear
if (( $index_start < 11 )); then
    echo '\n\nStarting script to analyse behavioural data...\n\n'
    python ${masterpath}/src_analysis/pre_analysis/behavioural_data_analysis_blind.py $1 $2 $3 $4
    echo '\n\nScript to analyse behavioural data DONE..\n\n'
fi

clear
if (( $index_start == 12 )); then
    echo '\n\nStarting script to analyse thermal imaging data...\n\n'
    python ${masterpath}/src_analysis/pre_analysis/thermal_imaging_analysis.py $1 $2 $3 $4
    echo '\n\nScript to analyse thermal imaging data DONE..\n\n'
fi