import subprocess
import os.path
import logging


MY_DIR = os.path.dirname(__file__)
SOURCES_DIR = MY_DIR + "/../greenlantern"
EXCLUDE_FILES = ()


class TestPep8():

    def test_pep8(self):
        popen = subprocess.Popen(
            ('pep8', '--ignore=E12,E24,E71', '--exclude={0}'.format(
                    ",".join(EXCLUDE_FILES)),
                SOURCES_DIR, MY_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        (stdout, stderr) = popen.communicate()
        if stdout != "":
            lines = stdout.split("\n")
            for line in lines:
                if line != "":
                    logging.error(line)
            assert False
