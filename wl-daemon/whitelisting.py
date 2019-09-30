import sys
import logging
from time import sleep, time
from .daemon import DaemonThread
from .test_framework.authproxy import JSONRPCException
from .connectivity import getoceand

BLOCK_TIME_DEFAULT = 60

class Whitelisting(DaemonThread):
    def __init__(self, conf):
    super().__init__()
    self.conf = conf
    self.ocean = getoceand(self.conf)
    self.interval = BLOCK_TIME_DEFAULT if "blocktime" not in conf else conf["blocktime"]
    self.logger = logging.getLogger(self.__class__.__name__)

    def run(self):
        while not self.stopped():
            sleep(self.interval - time() % self.interval)
            start_time = int(time())
            step = int(time()) % (self.interval * self.total) / self.interval

            height = self.get_blockcount()
            if height == None:
                continue

            self.logger.info("blockcount:{}".format(height))
            self.onboard_kycfiles()


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
        return rpc_func(self.ocean.onboarduser, kycfile)

    def onboard_kycfiles(self):
        # r=root, d=directories, f = files
        for r, d, f in os.walk(self.conf.kyc_indir):
            for file in f:
                path=os.path.join(r, file)
                try:
                    onboard_kycfile(path)
                except Exception as e:
                    self.logger.warning(e)
                    mess='when onboarding kycfile ' + path
                    self.logger.warning(mess)
                    return
                mess='onboarded kycfile ' + path
                self.logger.info(mess)
                outpath=os.path.join(self.conf.kyc_outdir, file)
                mess='moved kycfile ' + path + ' to ' + outpath 
                self.logger.info(mess)

                    
    

