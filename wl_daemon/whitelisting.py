import os
import sys
import logging
from time import sleep, time
from .daemon import DaemonThread
from .test_framework.authproxy import JSONRPCException
from .connectivity import getoceand

BLOCK_TIME_DEFAULT = 60
TRANSACTION_LIMIT = 1000

class Whitelisting(DaemonThread):
    def __init__(self, conf):
        super().__init__()
        self.conf = conf
        self.ocean = getoceand(self.conf)
        self.interval = BLOCK_TIME_DEFAULT if "blocktime" not in conf else conf["blocktime"]
        self.logger = logging.getLogger(self.__class__.__name__)
        self.init_status()
        self.previous_height = -1

    def init_status(self):
        self.towhitelist=set()
        self.whitelisted=set()
        self.toblacklist=set()
        self.blacklisted=set()
        self.pendingtx=set()

    #Returns true if there are no pending transactions
    def update_pendingtx(self):
        rmp_set=set()
        try:
            rmp=self.ocean.getrawmempool()
            rmp_set=set(rmp)
            del rmp[:]
        except Exception as e:
            self.logger.warning("getrawmempool error{}: {}".format(p, e))
            return False
        self.pendingtx=self.pendingtx.intersection(rmp_set)
        nPending=len(self.pendingtx)
        bNonePending=(nPending == 0)
        if bNonePending == False:
            self.logger.warning("update_pendingtx: {} pending".format(nPending))
        return bNonePending
        
    def update_files(self):
        self.towhitelist=set()
        self.logger.info("searching {} for kycfiles".format(self.conf["kyc_indir"]))
        for r, d, f in os.walk(self.conf["kyc_indir"]):
            for file in f:
                p=os.path.join(r, file)
                if not p in self.whitelisted:
                    self.towhitelist.add(p)

        self.toblacklist=set()
        self.logger.info("searching {} for kycfiles".format(self.conf["kyc_toblacklistdir"]))
        for r, d, f in os.walk(self.conf["kyc_toblacklistdir"]):
            for file in f:
                p=os.path.join(r, file)
                if p in self.towhitelist:
                    self.towhitelist.remove(p)
                if not p in self.blacklisted:
                    self.toblacklist.add(p)


        
    def update_status(self):
        self.logger.info("Updating status...")
        tmp=set()
        for f in self.towhitelist:
            if self.is_whitelisted(f):
                self.whitelisted.add(f)
                tmp.add(f)
            
        self.towhitelist=self.towhitelist.difference(tmp)
        self.blacklisted=self.blacklisted.difference(tmp)
        
        tmp=set()
        for f in self.toblacklist:
            if not self.is_whitelisted(f):
                self.blacklisted.add(f)
                tmp.add(f)
                       
        self.toblacklist=self.toblacklist.difference(tmp)
        self.whitelisted=self.whitelisted.difference(tmp)
        #toblacklist overrides towhitelist
        self.towhitelist=self.towhitelist.difference(self.toblacklist)
        self.logger.info("...finished updating status.")
        
        
    def is_whitelisted(self, p):
        try:
            bResult=self.ocean.validatekycfile(p)["iswhitelisted"]
            return bResult
        except Exception as e:
            self.logger.warning("Error validating kycfile{}: {}".format(p, e))
            return False
        
                
    def run(self):
        self.logger.info("Daemon started")
        while not self.stopped():
            sleep(self.interval - time() % self.interval)

            height = self.get_blockcount()
            self.logger.info("blockcount:{}".format(height))
            if height <= self.previous_height:
                continue
            if self.update_pendingtx() != True:
                continue
            self.update_files()
            self.update_status()
            self.onboard_kycfiles()
            self.blacklist_kycfiles()
            self.previous_height = height

    def rpc_retry(self, rpc_func, *args):
        for i in range(5):
            try:
                return rpc_func(*args)
            except Exception as e:
                self.logger.warning("{}\nReconnecting to client...".format(e))
                self.ocean = getoceand(self.conf)
        self.logger.error("Failed reconnecting to client")
        self.stop()
            
    def get_blockcount(self):
        return self.rpc_retry(self.ocean.getblockcount)

    def onboard_kycfile(self, kycfile):
        return self.ocean.onboarduser(kycfile)

    def onboard_kycfiles(self):
        self.logger.info("onboarding {} files".format(len(self.towhitelist)))
        for f in self.towhitelist:
            try:
                txid=self.onboard_kycfile(f)
                self.pendingtx.add(txid)
            except Exception as e:
                self.logger.error(e)
                mess='error when onboarding kycfile ' + f
                self.logger.error(mess)
                if hasattr(e, 'error'):
                    if 'message' in e.error:
                        if 'No whitelist asset available' in e.error['message']:
                            break
                continue
        
    def blacklist_kycfile(self, kycfile):
        return self.ocean.blacklistuser(kycfile)
                
    def blacklist_kycfiles(self):
        self.logger.info("blacklisting {} files".format(len(self.toblacklist)))
        for f in self.toblacklist:
            try:
                txid=self.blacklist_kycfile(f)
                self.pendingtx.add(txid)
            except Exception as e:
                self.logger.error(e)
                mess='error when blacklisting kycfile ' + f
                self.logger.error(mess)
                if hasattr(e, 'error'):
                    if 'message' in e.error:
                        if 'No whitelist asset available' in e.error['message']:
                            break
                continue


                    
    

