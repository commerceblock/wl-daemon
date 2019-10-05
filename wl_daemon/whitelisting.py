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

    def update_files(self):
        self.logger.info("searching {} for kycfiles".format(self.conf["kyc_indir"]))
        for r, d, f in os.walk(self.conf["kyc_indir"]):
            for file in f:
                if not file in self.whitelisted:
                    self.towhitelist.add(file)

        self.logger.info("searching {} for kycfiles".format(self.conf["kyc_toblacklistdir"]))
        for r, d, f in os.walk(self.conf["kyc_toblacklistdir"]):
            for file in f:
                if file in self.towhitelist:
                    self.towhitelist.remove(file)
                if not file in self.blacklisted:
                    self.toblacklist.add(file)
        
    def update_status(self):
        for f in self.towhitelist:
            if f in self.toblacklist:
                self.towhitelist.remove(f)
            p=os.path.join(self.conf["kyc_indir"], f)
            if self.is_whitelisted(p):
                self.whitelisted.add(f)
                self.towhitelist.remove(f)

        for f in self.toblacklist:
            p=os.path.join(self.conf["kyc_toblacklistdir"], f)
            if not self.is_whitelisted(p):
                self.blacklisted.add(f)
                self.toblacklist.remove(f)

    def is_whitelisted(self, p):
        try:
            bResult=self.ocean.validatekycfile(p)["iswhitelisted"]
            return bResult
        except Exception as e:
            self.logger.warning("Error validating kycfile:{}".format(e))
            return False
        
                
    def run(self):
        self.logger.info("Daemon started")
        while not self.stopped():
            sleep(self.interval - time() % self.interval)

            height = self.get_blockcount()
            if height == None:
                self.logger.info("blockcount:{}".format("None"))
                continue
            if height <= self.previous_height:
                self.logger.warning("blockcount:{} is not greater that previous blockcount:{}. Whitelist will not be updated.".format(height, self.previous_height))
                continue

            self.logger.info("blockcount:{}".format(height))
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
        self.logger.info("onboarding kycfiles")
        for f in self.towhitelist:
            p=os.path.join(self.conf["kyc_indir"], f)
            try:
                self.logger.info("onboarding file {}".format(p))
                self.onboard_kycfile(p)
            except Exception as e:
                self.logger.error(e)
                mess='error when onboarding kycfile ' + p
                self.logger.error(mess)
                continue
            mess='onboarded kycfile ' + p
            self.logger.info(mess)
        
    def blacklist_kycfile(self, kycfile):
        return self.ocean.blacklistuser(kycfile)
                
    def blacklist_kycfiles(self):
        self.logger.info("blacklisting kycfiles")
        for f in self.toblacklist:
            p=os.path.join(self.conf["kyc_toblacklistdir"], f)
            try:
                self.logger.info("blacklisting file {}".format(p))
                self.blacklist_kycfile(p)
            except Exception as e:
                self.logger.error(e)
                mess='error when blacklisting kycfile ' + p
                self.logger.error(mess)
                continue
            mess='blackclisted kycfile ' + p
            self.logger.info(mess)


                    
    

