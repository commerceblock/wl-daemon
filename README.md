# wl-daemon

Daemon for processing of kycfiles.

This will monitor a directory for kycfiles, onboard the addresses contained in the files, and move the files to a new location.

## Installation

    $ python3 setup.py build && python3 setup.py install

## Usage

    $ python3 wl-daemon.py --kycindir kycfiles_input_dir --kycoutdir kycfiles_output_dir --rpcconnect ocean_node_ip_addr --rpcport ocean_node_rpcport --user ocean_node_user_name --pass ocean_node_password 

