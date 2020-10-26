import argparse
from mca.pyside2_gui import main as pyside2_main


def main():
    parser = argparse.ArgumentParser(description='Execute the Multi Channel Analyzer')
    parser.add_argument("--pyside2_gui", "-g", type=str, nargs=1, choices=["pyside2"],
                        help='Choose the pyside2_gui for the mca', default="pyside2")

    args = vars(parser.parse_args())
    if args["pyside2_gui"] == "pyside2":
        pyside2_main.main()


if __name__ == '__main__':
    main()

