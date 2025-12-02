# BE AWARE OF DIRECTORY CALLS IN THIS SCRIPT!
# DIRECTORIES MUST BE HARDCODED

# dependencies:
# 	FSL (version 6.0.7.7)
# 	ANTs (version 2.5.1)
# 	AFNI (version 24.0.05)
# 	C3D (version 1.4.0)
# 	FreeSurfer (version 7.3.2)
# 	bids-validator (version 1.14.0)
# 	connectome-workbench (version 1.5.0)
 

#! /bin/bash
# This script will take DICOMS for BURNOUT and convert them into bids format

# get folder name and participant ID

#np=0
#maxjobs=16

raw_path=/rawdata
dev_path=/derivatives
work_dir=/work

# ! CHANGE DIRECTORY TO LICENSE !
# Export FreeSurfer license
export FS_LICENSE=/CHANGE DIRECTORY TO LICENSE LOCATION

# Find all subject folders
folders=$(find $raw_path -type d -name "sub-*")

# Loop through each subject folder
for f in $folders; do
    b=$(basename $f)
    subject=${b:4}
    echo "Processing subject: $subject"

    # Run fmriprep for each subject sequentially
    fmriprep-docker "$raw_path" \
        "$dev_path" \
        participant \
        --participant-label $subject \
        --fs-license-file "/license.txt" \
        --output-spaces MNI152NLin6Asym:res-2 fsaverage:res-native \
        --write-graph \
        --skip_bids_validation \
        --no-tty \
        --work-dir $work_dir \
        --verbose

    # Check if fmriprep finished successfully
    if [ $? -ne 0 ]; then
        echo "fMRIPrep failed for subject: $subject"
        exit 1
    fi
done

echo "All subjects processed."