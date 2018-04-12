import click
import subprocess
import sys

from clint.textui import colored, puts
from os import listdir
from os.path import isfile, join


def generate_results(input, py_file):
    with open(input) as infile:
        proc = subprocess.Popen(['python', py_file],
                                stdin=infile,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    out, err = proc.communicate()

    return out.decode(), err.decode()


def report_results(expected_str, actual_str):
    if expected_str == actual_str:
        puts(colored.green('Solution is correct!'))
    else:
        puts(colored.red('Incorrect!'))
        print(f'Expected output:\n{expected_str}\n'\
              f'Actual output:\n{actual_str}')


def get_files_from_path(path):
    files = [f for f in listdir(path) if isfile(join(path, f))]
    files.sort()
    return files


def print_header_report(case, input):
    print('=====================')
    print(f'Running case {case}:')
    with open(input) as input:
        for line in input.read().splitlines():
            print(line, end='\t')
    print()


def print_footer():
    print('=====================')
    print()


def report_case(assignment, exercise, input, case):
    solution = join('solutions', assignment, exercise)
    input = join('inputs', assignment, exercise[:-3], input)

    print_header_report(case, input)
    expected_out, _ = generate_results(input, solution)
    actual_out, _ = generate_results(input, exercise)
    report_results(expected_out, actual_out)
    print_footer()


@click.command()
@click.argument('assignment')
@click.argument('exercise')
def main(assignment, exercise):
    path = join('inputs', assignment, exercise[:-3])
    inputs = get_files_from_path(path)

    for case, input in enumerate(inputs, 1):
        report_case(assignment, exercise, input, case)


if __name__ == "__main__":
    main()
