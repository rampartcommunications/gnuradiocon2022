# Rampart Communications - PSK Toolbox

This repository is intended to provide simple examples for interacting
with [UBDM as a Service (UaaS)](https://ubdm-as-a-service.rampartcommunications.com).

## psk.py

usage: Encode or decode psk symbols [-h] (--encode | --decode) [--order ORDER] [--grey] [--output OUTPUT] filename

The psk.py file can be used to encode any file into a list of 32 bit floating point complex samples.

An example of encoding a file named hello.txt into out.fc32 would be the following

    python3 psk.py -e -o out.fc32 hello.txt

This would generate a file of QPSK points that can be plotted using the plotter.py file

    python3 plotter.py out.fc32

The hard decision (slicer) can be called on the out.fc32 file to get the original data file.
For example:

    python3 psk.py -d -o out.txt out.fc32

The out.txt file should exactly match the original hello.txt file.

## Using with UaaS

Take any data file and encode it with the psk.py

Example:

    python3 psk.py -e -o encoded.fc32 hello.txt

The encoded.fc32 file is a QPSK file.  Upload the encoded.fc32 file to the website.

Then an UBDM file can be downloaded.  The UBDM file can be plotted and the original encoded.fc32 can be plotted.

Example:

    python3 plotter.py encoded.fc32
    python3 plotter.py ubdm_download.fc32


Using any tools noise can be added to the fc32 file.  The ubdm_download_with_noise.fc32 can then be uploaded to the website.

The decoded download file is a new fc32 with the UBDM removed.  Plotting the downloaded file should show the original data with noise added.

Example:

    python3 plotter.py ubdm_decoded_download.fc32

To decode the original file, the psk.py script can be used.

    python3 psk.py -d -o out.txt ubdm_decoded_download.fc32

The bit errors when comparing out.txt with the orginal file should match the expected bit errors based on the noise you added to the psk symbols.