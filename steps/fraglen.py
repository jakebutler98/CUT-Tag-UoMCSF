########################################
# script for collecting the fragment length distribution 
# from the alignment phase

########################################

import os
import subprocess
import logging

def assess_fragment_lengths(Configuration):
    """
    Assess mapped fragment size distribution from the alignment SAM file.
    Extract the 9th column, compute absolute fragment lengths, and calculate the distribution.
    """
    # Paths
    sample_dir = os.path.join(Configuration.cleaned_alignments_dir, Configuration.file_to_process)
    fraglen_dir = os.path.join(Configuration.fraglength_dir)
    os.makedirs(fraglen_dir, exist_ok=True)

    input_sam = os.path.join(sample_dir, Configuration.file_to_process + "_bowtie2.sorted.sam")
    output_txt = os.path.join(fraglen_dir, Configuration.file_to_process + ".fragment_length.txt")
    
    # Ensure the input SAM file exists
    if not os.path.exists(input_sam):
        raise FileNotFoundError(f"Input SAM file not found: {input_sam}")
    
    logging.info(f"Assessing fragment lengths for {Configuration.file_to_process}")
    
    # Samtools and AWK command
    fraglen_command = f"""
    samtools view -F 0x04 {input_sam} |
    awk -F '\\t' 'function abs(x){{return ((x < 0.0) ? -x : x)}} {{print abs($9)}}' |
    sort | uniq -c |
    awk -v OFS="\\t" '{{print $2, $1/2}}' > {output_txt}
    """
    
    # Run the command
    logging.info(f"Running fragment length assessment command:\n{fraglen_command}")
    try:
        subprocess.run(fraglen_command, shell=True, check=True, executable="/bin/bash")
        logging.info(f"Fragment length distribution written to: {output_txt}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error in assessing fragment lengths: {e}")
        raise

    logging.info(f"Fragment length assessment completed for {Configuration.file_to_process}")