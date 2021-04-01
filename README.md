# Convert dicom directories to BIDS

Small wrapper for dcm2bids by @cbedetti for converting dicoms acquired by the
POND and KIND studies to BIDS. Based on work by Michael Joseph (@josephmje).
To use, clone this repository and create a python virtual environment in
the repository top level directory and install the requirements listed in
`requirements.txt`, then put the `<repo>/bin` directory on your path to
use `dcm2bids_conversion`. Example usage:

```sh
dcm2bids_conversion \
    -d SPReD \
    -b Queens_BIDS/ \
    -c POND-config.json \
    -g "PND03*MR" \
    -sr 'QNS_[0-9][0-9][0-9][0-9]' \
    -vr "_([0-9][0-9])_" \
    -ps "QNS" "394" \
    -psg "_" ""
```
