#!/usr/bin/env/python3
import os
import logging
import json
from .test_framework.authproxy import AuthServiceProxy, JSONRPCException
from .connectivity import getoceand, loadConfig

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rpconnect', required=True, type=str, help="Client RPC host")
    parser.add_argument('--rpcport', required=True, type=str, help="Client RPC port")
    parser.add_argument('--rpcuser', required=True, type=str, help="RPC username for client")
    parser.add_argument('--rpcpassword', required=True, type=str, help="RPC password for client")
    parser.add_argument('--kyc_indir', required=True, type=str, help="Dir containing kycfiles to be onboarded")
    parser.add_argument('--kyc_outdir', required=True, type=str, help="Destination of onboarded kycfiles")
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
    
    wl_daemon = Whitelisting(conf, nodes, inrate, inprd, inaddr, inscript, signer)
    wl_daemon.start()

    try:
        while 1:
            if signing_node.stopped():
                raise Exception("Node thread has stopped")
            time.sleep(0.01)
    except KeyboardInterrupt:
        signing_node.stop()

if __name__ == "__main__":
    main()
