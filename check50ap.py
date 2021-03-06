import click
import subprocess
import sys
import tempfile

from clint.textui import colored, puts
from os import listdir, remove
from os.path import isfile, join


def generate_results(py_file, input=None):
    if input is None:
        proc = subprocess.Popen(['python', py_file],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    else:
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


def print_header_report(case=None, input=None):
    print('=====================')
    if case:
        print(f'Running case {case}:')

    if input is not None:
        with open(input) as input:
            for line in input.read().splitlines():
                print(line, end='\t')
            print()


def print_footer():
    print('=====================')
    print()


def remove_silently(filename):
    try:
        remove(filename)
    except OSError:
        pass


def print_report(expected_out, actual_out, input, case=None):
    print_header_report(case, input)
    report_results(expected_out, actual_out)
    print_footer()


def report_case(assignment, exercise, input=None, case=None):
    solution = join('solutions', assignment, exercise)
    if input:
        input = join('inputs', assignment, exercise[:-3], input)

    expected_out, actual_out = generate_ouputs(solution, exercise, input)
    print_report(expected_out, actual_out, input, case)


def get_seed(seed_file):
    with open(join('inputs', 'random', seed_file)) as seed_file:
        seed = eval(seed_file.read())

    return seed


def write_file_with_fixed_seed(filename, tpm_filename, seed):
    random_header = f'import random\nrandom.seed({seed})\n'

    with open(filename) as f:
        f_str = f.read()
        with open(tpm_filename, 'w') as tmp:
            tmp.write(random_header + f_str)


def generate_ouputs(solution, exercise, input):
    expected, _ = generate_results(solution, input)
    actual, _ = generate_results(exercise, input)

    return expected, actual


def report_random_case(seed, case, assignment, exercise, input=None):
    if input:
        input = join('inputs', assignment, exercise[:-3], input)

    solution = join('solutions', assignment, exercise)
    tmp_solution = f's_{seed[:-4]}_{exercise}'
    tmp_exercise = f'e_{seed[:-4]}_{exercise}'
    seed = get_seed(seed)

    write_file_with_fixed_seed(solution, tmp_solution, seed)
    write_file_with_fixed_seed(exercise, tmp_exercise, seed)

    expected_out, actual_out = generate_ouputs(tmp_solution, tmp_exercise, input)
    remove_silently(tmp_solution)
    remove_silently(tmp_exercise)

    print_report(expected_out, actual_out, input, case)


def report_non_random_cases(inputs, assignment, exercise):
    if inputs:
        for case, input in enumerate(inputs, 1):
            report_case(assignment, exercise, input, case)
    else:
        report_case(assignment, exercise)


def report_random_cases(inputs, assignment, exercise):
    random_path = join('inputs', 'random')
    seeds = get_files_from_path(random_path)
    if inputs:
        for input in inputs:
            for case, seed in enumerate(seeds, 1):
                report_random_case(seed, case, assignment,
                                   exercise, input)
    else:
        for case, seed in enumerate(seeds, 1):
            report_random_case(seed, case, assignment, exercise)


@click.command()
@click.option('--no-input', is_flag=True)
@click.option('--random', is_flag=True)
@click.argument('assignment')
@click.argument('exercise')
def main(no_input, random, assignment, exercise):
    if no_input:
        inputs = []
    else:
        path = join('inputs', assignment, exercise[:-3])
        inputs = get_files_from_path(path)

    if random:
        report_random_cases(inputs, assignment, exercise)
    else:
        report_non_random_cases(inputs, assignment, exercise)


if __name__ == "__main__":
    main()
