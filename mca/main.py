import argparse

from mca.gui.pyside2 import main as pyside2_main


def main():
    parser = argparse.ArgumentParser(description='Execute the Multi Channel Analyzer')
    parser.add_argument("--pyside2", "-g", type=str, nargs=1, choices=["pyside2"],
                        help='Choose the pyside2 for the mca', default="pyside2")

    args = vars(parser.parse_args())
    if args["pyside2"] == "pyside2":
        pyside2_main.main()


if __name__ == '__main__':
    main()

