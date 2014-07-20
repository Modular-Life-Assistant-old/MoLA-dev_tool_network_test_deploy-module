from core import Daemon
from core import Log

import json
import os
import signal
import shutil
import subprocess
import uuid

class Module:
    def stop(self):
        self.__remove_files()
        self.__stop_mola()

    def thread_run__mola(self):
        self.__copy_files()
        self.__edit_network_config()
        self.__edit_web_interface_config()
        self.__start_mola()

    def __copy_files(self):
        self.__tmp_path = '/tmp/mola-%s/' % uuid.uuid4()

        shutil.copytree(
            Daemon.ROOT_PATH,
            self.__tmp_path,
            ignore=shutil.ignore_patterns(
                '*.pyc',
                '*.log',
                'dev_tool_*',
            )
        )

    def __edit_config(self, config_path, config):
        config_path = '%smodules/%s' % (self.__tmp_path, config_path)
        with open(config_path, 'w+') as file:
            file.write(json.dumps(config))

    def __edit_network_config(self):
        self.__edit_config(
            'mola_network/configs/network.json', 
            {
                'port': 12345,
            }
        )

    def __edit_web_interface_config(self):
        self.__edit_config(
            'web_interface/configs/web.json',
            {
                'port': 12346,
            }
        )

    def __remove_files(self):
        if self.__tmp_path:
            shutil.rmtree(self.__tmp_path)

    def __start_mola(self):
        try:
            self.__mola_process = subprocess.Popen(
                'python3 %sdaemon.py' % self.__tmp_path,
                stdout=subprocess.PIPE, 
                shell=True,
                preexec_fn=os.setsid
            )

        except Exception as e:
            Log.crash(e) 

    def __stop_mola(self):
        if self.__mola_process:
            os.killpg(self.__mola_process.pid, signal.SIGTERM)

