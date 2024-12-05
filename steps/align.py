########################################
# script for running the alignment of trimmed data
# bowtie2 is used, aligning to the hg38 genome

########################################

import os
import logging
import subprocess
import glob

def align(Configuration):
    """
    Function to align reads to the hg38 genome using bowtie2
    The options used are:
    --local --very-sensitive --no-mixed --no-discordant --phred33 -I 10 -X 700
    
    This means that the alignment is local, very sensitive, and does not allow for mixed or discordant alignments.
    The quality score is phred33, and the minimum and maximum insert sizes are 10 and 700, respectively.
    
    This will ignore any remaining adapter sequence at the 3' end of the reads.
    """
    
    trimmed_dir = os.path.join(Configuration.trimmed_dir)
    output_dir = os.path.join(Configuration.cleaned_alignments_dir, Configuration.file_to_process)
    os.makedirs(output_dir, exist_ok=True)
    
    forward_pattern = os.path.join(trimmed_dir, Configuration.file_to_process + "*1_trimmed.fq.gz")
    reverse_pattern = os.path.join(trimmed_dir, Configuration.file_to_process + "*2_trimmed.fq.gz")
    forward_reads = glob.glob(forward_pattern)
    reverse_reads = glob.glob(reverse_pattern)
    
    print("Forward Reads:", forward_reads)
    print("Reverse Reads:", reverse_reads)
    
    logging.info(f"Aligning reads for {Configuration.file_to_process}")
    
    # run bowtie2 on the trimmed data
    bowtie2_command = [
        "bowtie2", "--local", "--very-sensitive", "--no-mixed", "--no-discordant",
        "--phred33", "-I", "10", "-X", "700", "-p", "8",
        "-x", os.path.join(Configuration.bowtie2_index),
        "-1"
    ] + forward_reads + ["-2"] + reverse_reads + [
        "-S", os.path.join(output_dir, Configuration.file_to_process + ".sam")
    ]
    
    with open(os.path.join(output_dir, Configuration.file_to_process + "_bowtie2.txt"), "w") as log_file:
        subprocess.run(bowtie2_command, check=True, stdout=log_file, stderr=log_file)
    
    logging.info(f"Finished aligning reads for {Configuration.file_to_process}")
    

def align_spike_in(Configuration):
    """
    Function to align reads to the spike-in genome using bowtie2
    The purpose of the spike-in is to allow for normalization of the data.
    E. coli DNA is carried along with bacterially-produced pA-Tn5 protein and gets tagmented non-specifically during the reaction. 
    The fraction of total reads that map to the E.coli genome depends on the yield of epitope-targeted CUT&Tag, and so depends on the 
    number of cells used and the abundance of that epitope in chromatin. Since a constant amount of pATn5 is added to CUT&Tag reactions 
    and brings along a fixed amount of E. coli DNA, E. coli reads can be used to normalize epitope abundance in a set of experiments.
    
    The options used are:
    --end-to-end --very-sensitive --no-overlap --no-dovetail --no-mixed --no-discordant --phred33 -I 10 -X 700 -p 4
    
    This means that the alignment is end-to-end, very sensitive, and does not allow for overlap or dovetail alignments.
    The quality score is phred33, and the minimum and maximum insert sizes are 10 and 700, respectively.
    
    Dovetail alignments are when the two reads in a pair are aligned in the same direction but do not overlap. Presumably this is used for 
    spike in alignment because the spike in is a circular genome?
    """
    
    trimmed_dir = os.path.join(Configuration.trimmed_dir)
    output_dir = os.path.join(Configuration.cleaned_alignments_dir, Configuration.file_to_process)
    
    forward_pattern = os.path.join(trimmed_dir, Configuration.file_to_process + "*1_trimmed.fq.gz")
    reverse_pattern = os.path.join(trimmed_dir, Configuration.file_to_process + "*2_trimmed.fq.gz")
    forward_reads = glob.glob(forward_pattern)
    reverse_reads = glob.glob(reverse_pattern)
    
    print("Forward Reads:", forward_reads)
    print("Reverse Reads:", reverse_reads)
    
    logging.info(f"Aligning reads for {Configuration.file_to_process}")
    
    # run bowtie2 on the trimmed data
    bowtie2_command = [
        "bowtie2", "--end-to-end", "--very-sensitive", "--no-overlap", "--no-dovetail", "--no-mixed", "--no-discordant", 
        "--phred33", "-I", "10", "-X", "700", "-p", "4", 
        "-x", os.path.join(Configuration.bowtie2_index_spike_in), 
        "-1", 
    ]   + forward_reads + ["-2"] + reverse_reads + [ 
        "-S", os.path.join(output_dir, Configuration.file_to_process + "_spike_in.sam")
    ]    
        
    with open(os.path.join(output_dir, Configuration.file_to_process + "_bowtie2_spike_in.txt"), "w") as log_file:
        subprocess.run(bowtie2_command, check=True, stdout=True, stderr=log_file)
    
    logging.info(f"Finished aligning reads for {Configuration.file_to_process}")



def spike_seqDepth(Configuration):
    spike_file = os.path.join(Configuration.cleaned_alignments_dir, Configuration.file_to_process, Configuration.file_to_process + "_spike_in.sam")
    output_file = os.path.join(Configuration.cleaned_alignments_dir, Configuration.file_to_process, Configuration.file_to_process + "_spike_in.seqDepth")
    
    # Check if the spike-in SAM file exists
    if not os.path.exists(spike_file):
        raise FileNotFoundError(f"Spike-in SAM file not found: {spike_file}")
    
    # Run samtools view command
    samtools_command = ["samtools", "view", "-F", "0x04", spike_file]
    try:
        # Capture the output of the samtools command
        result = subprocess.run(samtools_command, check=True, capture_output=True, text=True)
        # Count the lines in the output
        seq_depth_double = len(result.stdout.strip().split("\n"))
        seq_depth = seq_depth_double // 2 
        
        # Write the sequence depth to the output file
        with open(output_file, "w") as f:
            f.write(str(seq_depth))
        
        print(f"Spike-in sequence depth calculated: {seq_depth}")
    except subprocess.CalledProcessError as e:
        print(f"Error running samtools: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise