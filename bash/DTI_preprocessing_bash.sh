
############
# Script for DTI image preprocessing (to be completed before TBSS or NODDI analysis)

# FSL command lines used:
# bet <input> <output> [options]
# eddy --imain=data --mask=my_hifi_b0_brain_mask --acqp=acqparams.txt --index=index.txt --bvecs=bvecs --bvals=bvals --topup=my_topup_results --out=eddy_corrected_data
# dtifit --data=data --mask=nodif_brain_mask --bvecs=bvecs --bvals=bvals --out=dti

# change the working directory to the folder that is one-level up of all your subjects folders : 

cd '/user/ YOUR WORKING DIRECTORY HERE'



# Step 1: locate Files
subjectPaths=`ls -d */DTI`

for subjectPath in $subjectPaths
do
    #S01 S02 ....
    subjectFolder=`basename "$(dirname "$subjectPath")"` 

    #S01/DTI/******DTI.nii
    image=${subjectPath}/*_DTI.nii
    indexFile=${subjectPath}/index.txt
    acqpFile=${subjectPath}/acqp.txt
    bvecFile=${subjectPath}/bvec.bvec
    bvalFile=${subjectPath}/bval.bval
   
   
    #Step 2: Bet the image, remove the skull
    if [ -z `find ${subjectPath} -name *_bet_mask.nii.gz` ]; then
        echo "==============${subjectFolder} starts================"
        bet ${image} ${subjectPath}/DTI_bet -m 
    else
        echo "==============${subjectFolder} starts================"
        echo "${subjectFolder}- Bet has done"  
    fi

    # Step 3 Eddy the images
    maskFile=`find ${subjectPath} -name *_bet_mask.nii.gz`
    imageFile=`find ${subjectPath} -name *_DTI.nii`
    
    if [ -z `find ${subjectPath} -name DTI_eddy.nii.gz` ]; then
        eddy_openmp --imain=${imageFile} --mask=${maskFile} --index=${indexFile} --acqp=${acqpFile} --bvecs=${bvecFile} --bvals=${bvalFile} --niter=5 --fwhm=10,0,0,0,0 --ol_nstd=3 --repol --out=${subjectPath}/DTI_eddy  
    else
        echo "${subjectFolder}- Eddy has done" 
    fi
    
    # Step 4 generate FA maps

    eddyFile=`find ${subjectPath} -name DTI_eddy.nii.gz`
    if [ -z `find ${subjectPath} -name *FA.nii.gz` ]; then
        dtifit --data=${eddyFile} --mask=${maskFile} --bvecs=${bvecFile} --bvals=${bvalFile} --out=${subjectPath}/${subjectFolder}_
        echo "==============${subjectFolder} ends=================="
    else    
        echo "${subjectFolder}- dtifit has done"
    fi

done

################
################

#Notes
