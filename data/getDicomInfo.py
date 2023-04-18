import pydicom
import os
import re
import argparse

def main(args):
  inputFile = args.inFile
  logFile = args.logFile
  with open(logFile, mode='w', encoding='utf-8') as f:

      nameparts = re.findall('De_(.+?)/', inputFile)
      readIn = pydicom.read_file(inputFile)
      #Print lines

      f.write("De_"+nameparts[0])	   #Patient Number
      f.write("\n")
      f.write(readIn[0x8,0x60].value)  #Modality DX/CT
      f.write("\n")
      try:
        f.write("0x1110"+readIn[0x18,0x1110].value) #distance from Source to Detector
      except:
        f.write(' ')
      f.write("\n")

      try:
        f.write("0x1111"+readIn[0x18,0x1111].value) #distance from Source to Patient
      except:
        f.write(' ')
      f.write("\n")
      try:
        f.write("PixelSpacing"+readIn[0x28,0x30].value[0]) #PixelSpacing
      except:
        f.write(' ')
      f.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--inFile',
                        help='input File path',
                        type=str,
                        default='')
    parser.add_argument('--logFile',
                        help='input logFile path',
                        type=str,
                        default='')


args = parser.parse_args()
main(args)

