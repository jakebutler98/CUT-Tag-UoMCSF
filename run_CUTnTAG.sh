#!/bin/bash --login
#$ -pe smp.pe 4
#$ -j y
#$ -o /mnt/jw01-aruk-home01/projects/oa_functional_genomics/projects/CUT_Tag/analyses/processing_pipeline/logs

#$ -t 1-2
INDEX=$((SGE_TASK_ID)) 

# change to the project directory
cd /mnt/jw01-aruk-home01/projects/oa_functional_genomics/projects/CUT_Tag

# Inform the app how many cores we requested for our job. The app can use this many cores.
# The special $NSLOTS keyword is automatically set to the number used on the -pe line above.
export OMP_NUM_THREADS=$NSLOTS

# activate all needed software
# done through activate_project script, but you're more than welcome to build your own conda environment, or just you the module load [software] command as needed
activate_project /mnt/jw01-aruk-home01/projects/oa_functional_genomics/projects/CUT_Tag
module load tools/java/1.8.0 # for picard

SAMPLE=$(awk "NR==$INDEX" /mnt/jw01-aruk-home01/projects/oa_functional_genomics/projects/CUT_Tag/analyses/processing_pipeline/scripts/samples.txt)

sleep $(($INDEX*20)) # stagger the start of the jobs to avoid crashing into each other
python /mnt/jw01-aruk-home01/projects/oa_functional_genomics/projects/CUT_Tag/analyses/processing_pipeline/scripts/main_CUTnTAG.py -i ${SAMPLE} -s heatmap

