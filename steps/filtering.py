########################################
# script for filtering alignment by mapping quality
# and convert file formats from sam to bam

########################################

import os
import subprocess
import logging

def filter_and_convert(Configuration, min_quality_score=2, bin_length=500):
    """
    Filters alignment results by mapping quality, converts file formats, and 
    prepares data for peak calling and visualization.

    Args:
        Configuration: Configuration object with paths and settings.
        min_quality_score (int): Minimum mapping quality score for filtering.
        bin_length (int): Bin size for replicate reproducibility assessment.
    """
    # Paths
    sample_dir = os.path.join(Configuration.cleaned_alignments_dir, Configuration.file_to_process)
    
    input_sorted_sam = os.path.join(sample_dir, Configuration.file_to_process + "_bowtie2.sorted.sam")
    input_sorted_rmdup_sam = os.path.join(sample_dir, Configuration.file_to_process + "_bowtie2.sorted.rmdup.sam")
    
    filtered_sam = os.path.join(sample_dir, Configuration.file_to_process + f"_bowtie2.sorted.filtered{min_quality_score}.sam")
    filtered_rmdup_sam = os.path.join(sample_dir, Configuration.file_to_process + f"_bowtie2.sorted.rmdup.filtered{min_quality_score}.sam")
    
    bam_file = os.path.join(sample_dir, Configuration.file_to_process + "_bowtie2.bam")
    rmdup_bam_file = os.path.join(sample_dir, Configuration.file_to_process + "_bowtie2.rmdup.bam")
    bed_file = os.path.join(sample_dir, Configuration.file_to_process + "_bowtie2.bed")
    filtered_bed = os.path.join(sample_dir, Configuration.file_to_process + "_bowtie2.filtered.bed")
    filtered_fragments_bed = os.path.join(sample_dir, Configuration.file_to_process + "_bowtie2.filtered.fragments.bed")
    filtered_bins_bed = os.path.join(sample_dir, Configuration.file_to_process + f"_bowtie2.filtered.fragments.bin{bin_length}.bed")
    
    # Ensure input files exist
    for input_file in [input_sorted_sam, input_sorted_rmdup_sam]:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Required input SAM file not found: {input_file}")
    
    # Command for filtering and conversion
    logging.info(f"Filtering and converting files for {Configuration.file_to_process}")
    
    try:
        # Step 1: Filter by mapping quality
        logging.info("Filtering by mapping quality...")
        filter_command_1 = f"samtools view -q {min_quality_score} -b {input_sorted_sam} > {filtered_sam}"
        filter_command_2 = f"samtools view -q {min_quality_score} -b {input_sorted_rmdup_sam} > {filtered_rmdup_sam}"
        subprocess.run(filter_command_1, shell=True, check=True, executable="/bin/bash")
        subprocess.run(filter_command_2, shell=True, check=True, executable="/bin/bash")
        
        # Step 2: Convert to BAM and BED formats
        logging.info("Converting file formats...")
        bam_command_1 = f"samtools view -bS -F 0x04 {filtered_sam} > {bam_file}"
        bam_command_2 = f"samtools view -bS -F 0x04 {filtered_rmdup_sam} > {rmdup_bam_file}"
        bed_command = f"bedtools bamtobed -i {bam_file} -bedpe > {bed_file}"
        subprocess.run(bam_command_1, shell=True, check=True, executable="/bin/bash")
        subprocess.run(bam_command_2, shell=True, check=True, executable="/bin/bash")
        subprocess.run(bed_command, shell=True, check=True, executable="/bin/bash")
        
        # Step 3: Filter BED file for same chromosome and fragment length < 1000bp
        logging.info("Filtering BED file...")
        filter_bed_command = f"awk '$1==$4 && $6-$2 < 1000 {{print $0}}' {bed_file} > {filtered_bed}"
        subprocess.run(filter_bed_command, shell=True, check=True, executable="/bin/bash")
        
        # Step 4: Extract fragment-related columns
        logging.info("Extracting fragment columns...")
        extract_columns_command = f"cut -f 1,2,6 {filtered_bed} | sort -k1,1 -k2,2n -k3,3n > {filtered_fragments_bed}"
        subprocess.run(extract_columns_command, shell=True, check=True, executable="/bin/bash")
        
        # Step 5: Assess replicate reproducibility
        logging.info("Binning for downstream assessment of replicate reproducibility...")
        bin_command = (
            f"awk -v w={bin_length} '{{print $1, int(($2 + $3)/(2*w))*w + w/2}}' {filtered_fragments_bed} | "
            f"sort -k1,1V -k2,2n | uniq -c | "
            f"awk -v OFS=\"\\t\" '{{print $2, $3, $1}}' | sort -k1,1V -k2,2n > {filtered_bins_bed}"
        )
        subprocess.run(bin_command, shell=True, check=True, executable="/bin/bash")
        
        logging.info(f"Filtering and conversion completed for {Configuration.file_to_process}")
    
    except subprocess.CalledProcessError as e:
        logging.error(f"Error during filtering or conversion for {Configuration.file_to_process}: {e}")
        raise
