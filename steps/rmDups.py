########################################
# script for removing duplicates from our data. 
# We are seeing high levels of duplication in our data so this may be necessary

# FROM HENIKOFF LAB:
# CUT&Tag integrates adapters into DNA in the vicinity of the antibody-tethered pA-Tn5, and the exact sites of integration are affected by the accessibility of surrounding DNA.
# For this reason fragments that share exact starting and ending positions are expected to be common, and such ‘duplicates’ may not be due to duplication during PCR. 
# In practice, we have found that the apparent duplication rate is low for high quality CUT&Tag datasets, and even the apparent ‘duplicate’ fragments are likely to be true fragments
# Thus, we DO NOT recommend removing the duplicates. In experiments with very small amounts of material or where PCR duplication is suspected, duplicates can be removed.

# FROM EPICYPHER 

########################################

import os
import logging
import subprocess
import glob

import os
import subprocess
import logging

def process_duplicates(Configuration):
    """
    Function to process duplicates using Picard tools.
    Includes sorting by coordinate, marking duplicates, and optionally removing duplicates.
    """
    # Paths
    sample_dir = os.path.join(Configuration.cleaned_alignments_dir, Configuration.file_to_process)
    summary_dir = os.path.join(Configuration.cleaned_alignments_dir, "picard_summary")
    os.makedirs(summary_dir, exist_ok=True)

    input_sam = os.path.join(sample_dir, Configuration.file_to_process + ".sam")
    sorted_sam = os.path.join(sample_dir, Configuration.file_to_process + "_bowtie2.sorted.sam")
    markdup_sam = os.path.join(sample_dir, Configuration.file_to_process + "_bowtie2.sorted.markdup.sam")
    markdup_metrics = os.path.join(summary_dir, Configuration.file_to_process + "_markdup_metrics.txt")
    rmdup_sam = os.path.join(sample_dir, Configuration.file_to_process + "_bowtie2.sorted.rmdup.sam")
    rmdup_metrics = os.path.join(summary_dir, Configuration.file_to_process + "_rmdup_metrics.txt")
    
    # Ensure input SAM file exists
    if not os.path.exists(input_sam):
        raise FileNotFoundError(f"Input SAM file not found: {input_sam}")
    
    logging.info(f"Processing duplicates for {Configuration.file_to_process}")
    
    # Sort by coordinate
    sort_command = [
        "java", "-jar", Configuration.picard, "SortSam",
        "I=" + input_sam,
        "O=" + sorted_sam,
        "SORT_ORDER=coordinate"
    ]
    logging.info(f"Running SortSam: {' '.join(sort_command)}")
    try:
        subprocess.run(sort_command, check=True)
        logging.info(f"Sorting complete: {sorted_sam}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error in SortSam: {e}")
        raise
    
    # Mark duplicates
    markdup_command = [
        "java", "-jar", Configuration.picard, "MarkDuplicates",
        "I=" + sorted_sam,
        "O=" + markdup_sam,
        "M=" + markdup_metrics
    ]
    logging.info(f"Running MarkDuplicates: {' '.join(markdup_command)}")
    try:
        subprocess.run(markdup_command, check=True)
        logging.info(f"MarkDuplicates complete: {markdup_sam}, metrics: {markdup_metrics}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error in MarkDuplicates: {e}")
        raise

    # Remove duplicates
    rmdup_command = [
        "java", "-jar", Configuration.picard, "MarkDuplicates",
        "I=" + sorted_sam,
        "O=" + rmdup_sam,
        "M=" + rmdup_metrics,
        "REMOVE_DUPLICATES=true"
    ]
    logging.info(f"Running RemoveDuplicates: {' '.join(rmdup_command)}")
    try:
        subprocess.run(rmdup_command, check=True)
        logging.info(f"RemoveDuplicates complete: {rmdup_sam}, metrics: {rmdup_metrics}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error in RemoveDuplicates: {e}")
        raise

    logging.info(f"Duplicate processing completed for {Configuration.file_to_process}")
