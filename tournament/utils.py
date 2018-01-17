from typing import List


def read_lines(file) -> List[str]:
    with open(file, 'r') as fp:
        lines = fp.readlines()
        lines = [line.rstrip('\n') for line in lines]

    return lines
