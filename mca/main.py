import argparse
import appdirs
import logging
import os

import mca
from mca.gui.pyside2 import main as pyside2_main


def main():
    """Main function of mca. Parses command line arguments and chooses a
    GUI to start.
    """
    log_folder = appdirs.user_log_dir(appname="mca")
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    logging.basicConfig(filename=os.path.join(log_folder, "mca.log"),
                        level=logging.INFO, filemode="w")
    parser = argparse.ArgumentParser(description='Execute the Multi Channel Analyzer')
    parser.add_argument("-g", "--gui", type=str, choices=["pyside2"],
                        help='Choose the gui for the mca', default="pyside2")
    parser.add_argument("-V", "--version", help='Get the version',
                        action='store_true', dest="version")
    args = vars(parser.parse_args())

    if args["version"]:
        mca_path = os.path.abspath(os.path.dirname(mca.__file__))
        with open(os.path.join(mca_path, 'version.txt')) as version_file:
            version = version_file.read()
        print("Multi Channel Analyzer Version: {}".format(version))
        return

    if args["gui"] == "pyside2":
        pyside2_main.main()


if __name__ == '__main__':
    main()

