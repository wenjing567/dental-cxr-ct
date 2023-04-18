#!/bin/bash
display_usage(){
        echo -e "\nUsage:  $0 [nifti file path] [CT log file from extractNifti.sh][workingDir][saveDir]"
        echo -e "\n  Eg: " 
        echo -e "\t $0 /home/user/patient1.nii.gz log_patient1.txt /home/lwj/file_data/testBox  imageDRR/imagetest"
        }
if [ $# -le 1 ]; then
        display_usage
        exit 1
fi

inputNii=${1}
ctlogfile=${2}
workingDir=${3}
saveDir=${4}
projM=`seq 5 1 10 | shuf | head -n1`
projL=`seq 25 1 30 | shuf | head -n1`
projR=-$projL
threshold=-1000

dim1=`awk 'NR==6 {print $1}' "$ctlogfile"`
dim2=`awk 'NR==6 {print $2}' "$ctlogfile"`
dim3=`awk 'NR==6 {print $3}' "$ctlogfile"`


niiFileName=`basename $inputNii`
fileDir=`dirname $inputNii`
filePrefix=${fileDir#*De_}
echo $filePrefix
subjID=${niiFileName%%.nii*}

logPath=${workingDir}/XLogs/De_${filePrefix}
if [[ ! -d $logPath ]]; then
	mkdir -p $logPath
fi
logFile=${logPath}/$subjID-drrlog.txt
echo $logFile
outputPathMiddle=${workingDir}/${saveDir}/De_${filePrefix}/middle
outputPathLeft=${workingDir}/${saveDir}/De_${filePrefix}/left
outputPathRight=${workingDir}/${saveDir}/De_${filePrefix}/right
if [[ ! -d $outputPathMiddle ]];then
     mkdir -p $outputPathMiddle
fi
if [[ ! -d $outputPathLeft ]];then
     mkdir $outputPathLeft
fi
if [[ ! -d $outputPathRight ]];then
     mkdir  $outputPathRight
fi
outputMPath=$outputPathMiddle/$subjID-drr.tif
outputLPath=$outputPathLeft/$subjID-drr.tif
outputRPath=$outputPathRight/$subjID-drr.tif
echo $outputMPath
ctInfo=${workingDir}/CTLogs/De_${filePrefix}/log_*"$subjID"_*.txt
dxInfo=${workingDir}/DXLogs/De_${filePrefix}/DX_log_*"$subjID"_*.txt
echo $ctInfo
echo $dxInfo
#Get DX distance
scpDist=$(( 1000 + (RANDOM % 5) )) #randomly add 0-5 mm to 1000mm, not sure if this is necessary or not
#else
	#scpDist=$(( $scpDist + (RANDOM % 2 - 1) ))


pix=`awk 'NR==5' $ctInfo`


# SET rotation for x, y, z, axes:
#rx=`seq 0 .01 1 | shuf | head -n1`
#ry=`seq 0 .01 1 | shuf | head -n1`
#rz=`seq 0 .01 1 | shuf | head -n1`
rx=0
ry=0
rz=0

# Set isocenter location
ix=$((${dim1}/2))
iy=$((${dim2}/2))
iz=`printf "%.0f" $(echo "scale=2;${dim3}/2" | bc)`
#ix=$(( ix + (RANDOM % 5 - 2) ))
#iy=$(( iy + (RANDOM % 5 - 2) ))
#iz=$(( iz + (RANDOM % 5 - 2) ))


reso=0.1

# since i'm setting the resolution pixel to be 0.1mm, the output image sizes should be multiple by the following factor
#factor=`echo "$pix/$reso" | bc`
imgW=240
imgH=120
w_s=0.25 
h_s=0.4
echo /home/lwj/ITK/ITK-bin/bin/TwoProjectionRegistrationTestDriver getDRRSiddonJacobsRayTracing -v -rp $projM -rx $rx -ry $ry -rz $rz -iso $ix $iy $iz -res 0.25 0.25 -size $imgW $imgH -scd $scpDist -threshold $threshold -o $outputMPath $inputNii
/home/lwj/ITK/ITK-bin/bin/TwoProjectionRegistrationTestDriver getDRRSiddonJacobsRayTracing -v -rp $projM -rx $rx -ry $ry -rz $rz -iso $ix $iy $iz -res $w_s $h_s -size $imgW $imgH -scd $scpDist -threshold $threshold -o $outputMPath $inputNii >> $logFile

echo /home/lwj/ITK/ITK-bin/bin/TwoProjectionRegistrationTestDriver getDRRSiddonJacobsRayTracing -v -rp $projL -rx $rx -ry $ry -rz $rz -iso $ix $iy $iz -res 0.25 0.25 -size $imgW $imgH -scd $scpDist -threshold $threshold -o $outputLPath $inputNii
/home/lwj/ITK/ITK-bin/bin/TwoProjectionRegistrationTestDriver getDRRSiddonJacobsRayTracing -v -rp $projL -rx $rx -ry $ry -rz $rz -iso $ix $iy $iz -res $w_s $h_s -size $imgW $imgH -scd $scpDist -threshold $threshold -o $outputLPath $inputNii >> $logFile

echo /home/lwj/ITK/ITK-bin/bin/TwoProjectionRegistrationTestDriver getDRRSiddonJacobsRayTracing -v -rp $projR -rx $rx -ry $ry -rz $rz -iso $ix $iy $iz -res 0.25 0.25 -size $imgW $imgH -scd $scpDist -threshold $threshold -o $outputRPath $inputNii
/home/lwj/ITK/ITK-bin/bin/TwoProjectionRegistrationTestDriver getDRRSiddonJacobsRayTracing -v -rp $projR -rx $rx -ry $ry -rz $rz -iso $ix $iy $iz -res $w_s $h_s -size $imgW $imgH -scd $scpDist -threshold $threshold -o $outputRPath $inputNii >> $logFile
