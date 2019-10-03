#!/usr/bin/env/python3
import os
import logging
import json
import argparse
import time
from .test_framework.authproxy import AuthServiceProxy, JSONRPCException
from .connectivity import getoceand, loadConfig
from .whitelisting import Whitelisting

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rpconnect', required=True, type=str, help="Client RPC host")
    parser.add_argument('--rpcport', required=True, type=str, help="Client RPC port")
    parser.add_argument('--rpcuser', required=True, type=str, help="RPC username for client")
    parser.add_argument('--rpcpassword', required=True, type=str, help="RPC password for client")
    parser.add_argument('--kyc_indir', required=True, type=str, help="Dir containing kycfiles to be onboarded")
    parser.add_argument('--kyc_outdir', required=True, type=str, help="Destination of onboarded kycfiles")
    parser.add_argument('--kyc_toblacklistdir', required=True, type=str, help="Dir containing kycfiles to be blacklisted")
    parser.add_argument('--kyc_blacklisteddir', required=True, type=str, help="Destination of blacklisted kycfiles")
    return parser.parse_args()

def main():
    args = parse_args()

    logging.basicConfig(
        format='%(asctime)s %(name)s:%(levelname)s:%(process)d: %(message)s',
        level=logging.INFO
    )

    conf = {}
    conf["rpcuser"] = args.rpcuser
    conf["rpcpassword"] = args.rpcpassword
    conf["rpcport"] = args.rpcport
    conf["rpcconnect"] = args.rpconnect
    conf["kyc_indir"] = args.kyc_indir
    conf["kyc_outdir"] = args.kyc_outdir
    conf["kyc_toblacklistdir"] = args.kyc_toblacklistdir
    conf["kyc_blacklisteddir"] = args.kyc_blacklisteddir
    
    
    wl_daemon = Whitelisting(conf)
    wl_daemon.start()

    try:
        while 1:
            if wl_daemon.stopped():
                raise Exception("Node thread has stopped")
            time.sleep(0.01)
    except KeyboardInterrupt:
        wl_daemon.stop()

if __name__ == "__main__":
    main()
