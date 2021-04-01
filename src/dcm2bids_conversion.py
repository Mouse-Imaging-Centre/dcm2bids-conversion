#!/usr/bin/env python3

# dcm2bids from https://github.com/cbedetti/Dcm2Bids
# relies on config file

import os
import os.path
from glob import glob
import subprocess
import argparse
import re

script_dir = os.path.dirname(os.path.realpath(__file__))

configs = glob(script_dir + "/*.json")
configs_rel = "\n".join([ os.path.basename(c) for c in configs ])

parser = argparse.ArgumentParser(description = """
  Convert a directory containing dicoms arranged into series sub-directories into a BIDS directory.
""")
parser.add_argument("--dicomdir", "-d", help = "The directory full of dicoms", required = True)
parser.add_argument("--bidsdir", "-b", help = "The directory in which to create the BIDS subject directory", required = True)
parser.add_argument("--config", "-c", required = True, help ="""
Configuration to use, can either be one of 
{}
or a path to a custom configuration file
""".format(configs_rel))
parser.add_argument("--glob", "-g", help = "A glob identifying subject directories (run inside the dcmdir. Remember to quote", required = True)
parser.add_argument("--subject", "-sr"
                    , help = "A regex identifying a subject code in the directory. If the regex "
                              "contains a capture group, use first the capture group, Default is the "
                              "All characters between the first and last '-' or '_' - '[-_](.*)[-_]' note"
                              "the use of a capture group"
                    , default = "[-_](.*)[-_]")
parser.add_argument("--postproc-subject", "-ps"
                    , help = "A space separated pair of regex patterns and replacements to perform on the"
                             " subject names. Identified by `--subject` e.g. `-ps 'QNS 394'`, this argument"
                             " may be passed multiple times."
                    , action = "append", nargs = 2)
parser.add_argument("--postproc-subject-global", "-psg"                
                    , help = "The same as --postproc-subject but performing global replacement"
                    , action = "append", nargs = 2)         
parser.add_argument("--visit", "-vr"
                    , help = "A regex identifying a visit code for the subject. "
                             "Defaults to None, where all subjects are coded as visit 1")
parser.add_argument("--remove-separators", action = "store_true"
                    , help = "Whether to remove separators '-' and '_' from the subject codes. "
                             "This is done after both postproc arguments.")
                    
args = parser.parse_args()

dcm_dir = args.dicomdir
cfg_file = args.config
bids_dir = args.bidsdir

def search_capture_group(reg, string):
    m_obj = re.search(reg, string)
    if m_obj is None:
        return None
    try:
        return m_obj.group(1)
    except IndexError:
        return m_obj.group(0)
       

if not os.path.exists(dcm_dir):
    parser.error("--dcmdir path not found")

if not os.path.exists(bids_dir):
    parser.error("--bidsdir path not found")

if not os.path.exists(cfg_file):
    cfg_file_global = os.path.join(script_dir, "configs", cfg_file)
    if not os.path.exists(cfg_file_global):
        parser.error("""
        --config {} not found in the current directory, nor in the script directory {}.
        """.format(cfg_file, script_dir))
    cfg_file = cfg_file_global

subject_dirs = glob(dcm_dir + '/' + args.glob)

if len(subject_dirs) == 0:
    parser.error("--glob no subjects in {} match glob {}".format(dcm_dir, args.glob))

for subject_dir in subject_dirs:
    session_label = os.path.basename(subject_dir)
    subject = search_capture_group(args.subject, session_label)
    print(subject)
    assert subject is not None, (
        "--subject/-sr regex '{}' failed to match for session {}".format(args.subject, session_label)
        )
        
    if args.visit is None:
        visit = "01"
    else:
        m = search_capture_group(args.visit, session_label)
        assert m is not None, (
            "--visit/-vr regex '{}' didn't match for session {}".format(args.visit, session_label)
        )
        visit = m.zfill(2)

    if args.postproc_subject:
        for (reg, rep) in args.postproc_subject:
            subject = re.sub(reg, rep, subject, count = 1)

    if args.postproc_subject_global:
        for (reg, rep) in args.postproc_subject_global:
            subject = re.sub(reg, rep, subject)

    if args.remove_separators:
        subject = re.sub("[-_]", "", subject)

    new_dir = '{}/tmp_dcm2bids/sub-{}_ses-{}'.format(bids_dir, subject, visit)
    sub_dir = "{}/sub-{}/ses-{}".format(bids_dir,subject,visit)
    if not os.path.exists(new_dir) and not os.path.exists(sub_dir):
        print("running: " + new_dir)
        subprocess.call(["dcm2bids", "-d", subject_dir, "-p", subject, "-s", visit, "-c", cfg_file, "-o", bids_dir])
    else:
        print("skipping: " + new_dir)
