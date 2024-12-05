########################################
# script for performing macs2 peak calling

########################################

import os
import subprocess
import logging

def narrow_peak_calling(Configuration):
    """
    Perform narrow peak calling using MACS2 for transcription factors (TFs).
    """

    # Set directories and files
    sample_dir = os.path.join(Configuration.cleaned_alignments_dir, Configuration.file_to_process)
    macs2_narrow_dir = os.path.join(Configuration.macs2_narrow_dir, Configuration.file_to_process)
    os.makedirs(macs2_narrow_dir, exist_ok=True)

    # Define file paths
    input_bam = os.path.join(sample_dir, f"{Configuration.file_to_process}_bowtie2.bam")

    # Check if the BAM file exists
    if not os.path.exists(input_bam):
        raise FileNotFoundError(f"BAM file not found: {input_bam}")

    # MACS2 command for narrow peak calling
    narrow_peak_command = [
        "macs2", "callpeak", "-t", input_bam,
        "-g", "hs", "-f", "BAMPE", "-n", f"macs2_narrowpeak_q0.01",
        "--outdir", macs2_narrow_dir, "--qvalue", "0.01", "-B", "--SPMR",
        "--keep-dup", "all"
    ]
    
    # Run the narrow peak calling command
    logging.info(f"Running MACS2 narrow peak calling command: {' '.join(narrow_peak_command)}")
    try:
        subprocess.run(narrow_peak_command, check=True)
        logging.info(f"Narrow peak calling completed. Results saved to: {macs2_narrow_dir}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error in narrow peak calling: {e}")
        raise

def broad_peak_calling(Configuration):
    """
    Perform broad peak calling using MACS2 for histone modifications.
    """

    # Set directories and files
    sample_dir = os.path.join(Configuration.cleaned_alignments_dir, Configuration.file_to_process)
    macs2_broad_dir = os.path.join(Configuration.macs2_broad_dir, Configuration.file_to_process)
    os.makedirs(macs2_broad_dir, exist_ok=True)

    # Define file paths
    input_bam = os.path.join(sample_dir, f"{Configuration.file_to_process}_bowtie2.bam")

    # Check if the BAM file exists
    if not os.path.exists(input_bam):
        raise FileNotFoundError(f"BAM file not found: {input_bam}")

    # MACS2 command for broad peak calling
    broad_peak_command = [
        "macs2", "callpeak", "-t", input_bam,
        "-g", "hs", "-f", "BAMPE", "-n", f"macs2_broadpeak_q0.01",
        "--outdir", macs2_broad_dir, "--qvalue", "0.01", "-B", "--broad", "--broad-cutoff", "0.1", "--SPMR",
        "--keep-dup", "all"
    ]
    
    # Run the broad peak calling command
    logging.info(f"Running MACS2 broad peak calling command: {' '.join(broad_peak_command)}")
    try:
        subprocess.run(broad_peak_command, check=True)
        logging.info(f"Broad peak calling completed. Results saved to: {macs2_broad_dir}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error in broad peak calling: {e}")
        raise