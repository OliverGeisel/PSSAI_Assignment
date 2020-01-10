import sys

from src.decoder import parse_tasks


def run(*args):
    parse_tasks(args[1])


if __name__ == "__main__":
    run(*sys.argv)
