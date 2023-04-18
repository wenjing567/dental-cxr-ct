#!/bin/bash
display_usage(){
        echo -e "\nUsage:  $0 [startIndex] [endIndex] [workingDir] [srcDir] [saveDir]"
        echo -e "\n  Eg: to convert CT (in nifti format) to synthetic Xray or drr for patient 1 to 10 run the line below:" 
        echo -e "\t $0 1 10 /home/lwj/file_data/testBox boxRes/imagetest boxRes/imageDrr"
        }
if [ $# -le 1 ]; then
        display_usage
        exit 1
fi
declare -i startI
declare -i endI
startI=${1}
endI=${2}
workingDir=${3}
srcDir=${4}
saveDir=${5}

filearr=()
#workingDir=/home/lwj/file_data/testBox

cd $workingDir
for fileLoc in `ls -rt "$PWD/$srcDir"`;  do
    echo ${fileLoc}
    filearr[${#filearr[*]}]=${fileLoc}
done
for i in $(seq $startI $endI ); do
	namepart=${filearr[i]}
  for file in `ls -rt "$PWD/$srcDir/$namepart/sixCm"`;  do
    filePrefix=${file%%.*}
    echo $filePrefix
    str2="raw"
    if [[ $filePrefix == *$str2* ]];then
      echo ''
    else
      fileLoc=$srcDir/$namepart/sixCm/${file}
      echo fileLoc
      ctlog=`ls CTLogs/$namepart/sixCm/log_"${filePrefix}"_*.txt`
      echo $ctlog
      pwd
      /home/lwj/al-ct-x-multi/data/itkDRR.sh $fileLoc $ctlog $workingDir $saveDir
    fi
  done
done
