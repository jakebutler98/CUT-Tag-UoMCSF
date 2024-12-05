########################################
# script for running the QC of raw data,
# trimming, and QC of trimmed data

########################################

import os
import logging
import subprocess
import glob

def qc_raw(Configuration):
    """
    Function to run QC on raw data
    """
    input_dir = os.path.join(Configuration.RAW_input_dir,Configuration.file_to_process)
    output_dir = os.path.join(Configuration.QC_dir_raw,Configuration.file_to_process)
    os.makedirs(output_dir,exist_ok=True)
    
    forward_pattern = os.path.join(input_dir, Configuration.file_to_process + "_*_1.fq.gz")
    reverse_pattern = os.path.join(input_dir, Configuration.file_to_process + "_*_2.fq.gz")
    forward_reads = glob.glob(forward_pattern)
    reverse_reads = glob.glob(reverse_pattern)
    
    print("Forward Reads:", forward_reads)
    print("Reverse Reads:", reverse_reads)
    
    logging.info(f"Running QC on raw data for {Configuration.file_to_process}")
    
    # run fastqc on the raw data 
    fastqc_command = ["fastqc", "-t", "4", "-o", output_dir] + forward_reads + reverse_reads
    subprocess.run(fastqc_command, check=True, capture_output=True, text=True)

    
    logging.info(f"Finished running QC on raw data for {Configuration.file_to_process}")
    

def trim_reads(Configuration):
    """
    Function to trim reads.
    The lab that developed CUT&Tag perform single-index 25x25 PE Illumina sequencing.
    This means that they have no need to perform trimming.
    However, we work closely with NovaGene, who perform 150x150 PE Illumina sequencing.
    As such, we need to trim the reads at approximately 40bp to remove adapter sequence and low quality bases.
    Here, we use Cutadapt to trim the reads.
    """
    
    os.makedirs(Configuration.trimmed_dir,exist_ok=True)
    
    input_dir = os.path.join(Configuration.RAW_input_dir,Configuration.file_to_process)
    
    
    forward_pattern = os.path.join(input_dir, Configuration.file_to_process + "_*_1.fq.gz")
    reverse_pattern = os.path.join(input_dir, Configuration.file_to_process + "_*_2.fq.gz")
    forward_reads = glob.glob(forward_pattern)
    reverse_reads = glob.glob(reverse_pattern)
    forward_trimmed = os.path.join(Configuration.trimmed_dir, Configuration.file_to_process + "_1_trimmed.fq.gz")
    reverse_trimmed = os.path.join(Configuration.trimmed_dir, Configuration.file_to_process + "_2_trimmed.fq.gz")
    
    logging.info(f"Trimming reads for {Configuration.file_to_process}")
    
    cutadapt_command = ["cutadapt", "-l", "40", "-j", "4", "-o", forward_trimmed, "-p", reverse_trimmed] + forward_reads + reverse_reads
    
    subprocess.run(cutadapt_command, check=True, capture_output=True, text=True)
    
    logging.info(f"Finished trimming reads for {Configuration.file_to_process}")
    
def qc_trimmed(Configuration):
    """
    Function to run QC on trimmed data
    """
    input_dir = Configuration.trimmed_dir
    output_dir = os.path.join(Configuration.QC_dir_trimmed,Configuration.file_to_process)
    os.makedirs(output_dir,exist_ok=True)
    
    forward_trimmed = os.path.join(input_dir, Configuration.file_to_process + "_1_trimmed.fq.gz")
    reverse_trimmed = os.path.join(input_dir, Configuration.file_to_process + "_2_trimmed.fq.gz")
    
    logging.info(f"Running QC on trimmed data for {Configuration.file_to_process}")
    
    # run fastqc on the trimmed data
    fastqc_command = ["fastqc", "-t", "4", "-o", output_dir, forward_trimmed, reverse_trimmed]
    subprocess.run(fastqc_command, check=True, capture_output=True, text=True)
        
    logging.info(f"Finished running QC on trimmed data for {Configuration.file_to_process}")
    