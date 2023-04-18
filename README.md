# dental-cxr-ct
Generation of periapical radiographs from CBCT
## background
This project extracts information from CBCT to generate a dental radiograph for each tooth. Firstly, a labeled file is needed to annotate the location of each tooth in the CBCT image, and then the teeth are segmented according to the labeled file. The segmented teeth are then subjected to simulated illumination using code to generate dental radiographs, and finally, root apex films are generated. This project extracts information from CBCT to generate a dental image for each tooth. First, a labeling file is needed to mark the position of each tooth in the CBCT image, and then the teeth are segmented based on the labeling file. Then, the code simulates the illumination and cuts out the teeth, generating three different angles of dental images of the root apex. The code that simulates the lighting to generate X-rays mainly comes from [KendallPark/cxr-ct](https://github.com/KendallPark/cxr-ct/tree/master/data).
## install
If interested to run the scripts here, change all directories to your local directories.
This set of scripts will need python modules: (1)dicom2nifit, (2)dipy, (3)pydicom, (4)nibbabel and ITK (only needed for creating synthetic xray)
## Usage
`python multi_threading_slice.py`

