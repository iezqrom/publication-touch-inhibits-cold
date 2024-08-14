#!/bin/sh

./src_testing/experiment.sh $@
# ./src_testing/lut/lut.sh -s tb
rm nohup.out

# for i in ./src_testing/*;
# do
# echo $i
# chown ivanezqrom $i;
# chmod a+rx $i;
# done
