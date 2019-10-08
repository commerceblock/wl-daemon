# wl-daemon

Daemon for processing of kycfiles.

This will monitor a directory for kycfiles, and onboard the addresses contained in the files.

Addresses can be blacklisted by moving the file to the /"tobalcklist/" folder

## Installation

    $ python3 setup.py build && python3 setup.py install

## Usage

    $ ./run_wl_daemon --kyc_indir kycfiles_input_dir --toblacklistdir kyc_blacklist_dir --rpcconnect ocean_node_ip_addr --rpcport ocean_node_rpcport --rpcuser ocean_node_user_name --rpcpassword ocean_node_password 

