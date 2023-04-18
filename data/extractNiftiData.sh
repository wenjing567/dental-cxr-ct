#!/bin/bash
display_usage(){
	echo -e "\nUsage:  $0 [fileName][startIndex][endIndex][workingDir][outputLoc]"
	echo -e "\n  Eg: to convert dicom to nifti for patient 1 to 10 run the line below:" 
	echo -e "\t $0 /home/lwj/file_slice/miuxiuxia 1 10 /home/lwj/file_data/testBox boxRes/gamma /home/lwj/al-ct-x/data"
	}
if [ $# -le 1 ]; then
	display_usage
	exit 1
fi

declare -i count
declare -i startI
declare -i endI
declare fileName
fileName=${1}
startI=${2}
endI=${3}
workingDir=${4}
outputLoc=$workingDir/${5}
repoDir=${6}
filearr=()

echo $outputLoc

if [[ ! -d $outputLoc ]]; then
	mkdir -p $outputLoc
fi

cd $fileName
for fileLoc in `ls -rt "$PWD"`;  do
    filearr[${#filearr[*]}]=${fileLoc}
done

for i in $(seq $startI $endI ); do
    cd ${fileName}/${filearr[i]}
    for fileLoc in `ls -rt "${fileName}/${filearr[i]}"`;  do
      cd ${fileName}/${filearr[i]}/${fileLoc}
      ctlogDir="$workingDir/CTLogs/${filearr[i]}/${fileLoc}"
      dxlogDir="$workingDir/DXLogs/${filearr[i]}/${fileLoc}"
      echo ${ctlogDir}
      echo ${dxlogDir}
      if [[ ! -d $ctlogDir ]]; then
        mkdir -p $ctlogDir
      fi
      if [[ ! -d $dxlogDir ]]; then
        mkdir -p $dxlogDir
      fi
      for files in `ls -rt "${fileName}/${filearr[i]}/${fileLoc}"`;  do
        cd ${fileName}/${filearr[i]}/${fileLoc}/${files}
        targetFile=`find "$PWD" -name "Slice_0000.dcm"`
        echo "$PWD"
        outlist=`ls $targetFile -1 | wc`
        outcount=`echo "$outlist" | awk '{ print $1;}'` #number of files...
        count=0
        if [[ "$outcount" -ge 1 ]]; then
          while IFS=" " read -ra arr; do

            for j in "${arr[@]}"; do
              (( count += 1 ))
              echo $j
              echo "$count"
              if [[ -f "$j" ]]; then
                targetDir=$(dirname "$j")
                valueLog="$ctlogDir/log_${files}_${count}.txt"
                echo ${repoDir}/getDicomInfo.py --inFile "${j}" --logFile "${valueLog}"
                echo ${valueLog}
                python ${repoDir}/getDicomInfo.py --inFile "${j}" --logFile "${valueLog}"
                ct_val=`awk 'NR==2' $valueLog`
                stp_val=`awk 'NR==4' $valueLog`

                if [[ "$ct_val" == "CT" ]]; then
                  python3 ${repoDir}/preproc_nifti.py --inDir "${targetDir}" --out "${outputLoc}" --logFile "$valueLog"
                else
                  mv $valueLog ${valueLog/log/DX_log}
                fi
              fi
            done
          done <<< "${targetFile}"
        fi
      done
    done
  done
cd $workingDir
mv DX_log* $dxlogDir

