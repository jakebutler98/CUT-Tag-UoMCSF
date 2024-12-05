########################################
# main script that calls all functions

# naming system:


# designed to work specifically for our library preparation methods
# only usable with paired end reads

########################################

from configuration import Config
import os
import glob
from random import random
from time import sleep
import argparse
import logging
from steps import qc_trim_qc, align, rmDups, fraglen, filtering, calibration, peak_calling, heatmap


# main function
if __name__=="__main__":
    
    parser = argparse.ArgumentParser(description='Wrapper function for all steps of CUTnTAG pipeline')
    
    parser.add_argument('-i', '--input', dest='infile', action='store', required=False,
                        help='Input folderto force. Will overwrite all outputs')
    parser.add_argument("-s",'--steps', dest='step', action='append', required=False,
                        help='chose steps instead of running everything')
    
    # parse arguments
    args = parser.parse_args()
    
    # set up configuration object for all steps. this sets up logging as well
    Configuration = Config()
    
    if args.infile == None:
        all_raws_present = [os.path.basename(x) for x in glob.glob(Configuration.RAW_input_dir)]

        all_processed = [os.path.basename(x) for x in glob.glob(Configuration.cleaned_alignments_dir)]
        # chose the first one of the ones that are still not processed and run 
        for i in all_raws_present:
            if i not in all_processed:
                os.makedirs(os.path.join(Configuration.cleaned_alignments_dir,i),exist_ok=True)
                Configuration.file_to_process = i
                break

        if Configuration.file_to_process == None:
            logging.error("There were no new files to process")
            raise Exception
        
    else:
        Configuration.file_to_process = args.infile
        os.makedirs(os.path.join(Configuration.cleaned_alignments_dir,Configuration.file_to_process),exist_ok=True)
    
    logging.info(f"This script will run the file : {Configuration.file_to_process}")
    
    if args.step == None:
        # call QC and trimming
        qc_trim_qc.qc_raw(Configuration)
        qc_trim_qc.trim_reads(Configuration)
        qc_trim_qc.qc_trimmed(Configuration)
        
        # alignment to hg38 and spike E. coli for normalization
        align.align(Configuration)
        align.align_spike_in(Configuration)
        align.spike_seqDepth(Configuration)
        
        # deduplication and duplication metrics
        rmDups.process_duplicates(Configuration)
        
        # fragment length distribution
        fraglen.assess_fragment_lengths(Configuration)
        
        # filtering of alignment
        filtering.filter_and_convert(Configuration) # default args are min_quality_score=2, bin_length=500
        
        # calibration to spike in
        calibration.spike_in_calibration(Configuration)
        
        # macs2 peak calling
        peak_calling.narrow_peak_calling(Configuration)
        peak_calling.broad_peak_calling(Configuration)
        
        # Visualization of peaks - heatmaps
        heatmap.generate_bigwig(Configuration)
        heatmap.compute_matrix_and_plot(Configuration)
        heatmap.generate_summit_regions_and_compute_matrix(Configuration)
        
        
        
        
        
        
    else:
        if "qc_raw" in args.step:
            qc_trim_qc.qc_raw(Configuration)
        if "trim_reads" in args.step:
            qc_trim_qc.trim_reads(Configuration)
        if "qc_trimmed" in args.step:
            qc_trim_qc.qc_trimmed(Configuration)
        if "align" in args.step:
            align.align(Configuration)
        if "align_spike" in args.step:
            align.align_spike_in(Configuration)
            align.spike_seqDepth(Configuration)
        if "remove_dups" in args.step:
            rmDups.process_duplicates(Configuration)
        if "fragLen" in args.step:
            fraglen.assess_fragment_lengths(Configuration)
        if "filter" in args.step:
            filtering.filter_and_convert(Configuration) # default args are min_quality_score=2, bin_length=500
        if "calibrate" in args.step:
            calibration.spike_in_calibration(Configuration)
        if "narrow_peak" in args.step:
            peak_calling.narrow_peak_calling(Configuration)
        if "broad_peak" in args.step:
            peak_calling.broad_peak_calling(Configuration)
        if "heatmap" in args.step:
            heatmap.generate_bigwig(Configuration)
            heatmap.compute_matrix_and_plot(Configuration)
            heatmap.generate_summit_regions_and_compute_matrix(Configuration)
