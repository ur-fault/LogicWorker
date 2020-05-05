# RandomTruthTableGenerator.py
import os
from os import path
from random import getrandbits
from tqdm import tqdm

print_func = print
print_output = True


def generate_table(input_count, output_count):
    rows = []

    def run(x):
        xbin = f'{x:b}'
        inp = []
        for char in xbin:
            if char == '0':
                inp.append(False)
            else:
                inp.append(True)
        rows.append(([False] + inp[1:], [not not getrandbits(1)
                                         for x in range(output_count)]))
        del xbin

    if input_count == 0:
        return []
    elif input_count == 1:
        return [([False], [not not getrandbits(1) for x in range(output_count)]), ([True], [not not getrandbits(1) for x in range(output_count)])]
    bin_len = '1' + '0' * (input_count - 1)
    print_to_console('Preparing combinations...')

    if print_output:
        for x in tqdm(range(int(bin_len, 2), int(bin_len, 2) * 2)):
            run(x)
    else:
        for x in range(int(bin_len, 2), int(bin_len, 2) * 2):
            run(x)
    print_to_console('Combinations prepared')
    next_rows = []
    print_to_console('Preparing non-one in first position of number...')
    if print_output:
        for row in tqdm(rows):
            next_rows.append(
                ([True] + row[0][1:], [not not getrandbits(1) for x in range(output_count)]))
    else:
        for row in rows:
            next_rows.append(
                ([True] + row[0][1:], [not not getrandbits(1) for x in range(output_count)]))
    rows.extend(next_rows)
    del next_rows

    return rows


def save_table(p, table):
    def run(row):
        inputs_to_write = []
        outputs_to_write = []
        for inp in row[0]:
            if inp:
                inputs_to_write.append('1')
            else:
                inputs_to_write.append('0')
        for out in row[1]:
            if out:
                outputs_to_write.append('1')
            else:
                outputs_to_write.append('0')
        lines.append(','.join(inputs_to_write) +
                     ' ' + ','.join(outputs_to_write))
        del inputs_to_write

    if path.exists(p):
        os.remove(p)

    lines = []
    os.makedirs(path.realpath(path.split(p)[0]), exist_ok=True)
    print_to_console('Preparing to save...')
    if print_output:
        for row in tqdm(table):
            run(row)
    else:
        for row in table:
            run(row)
    print_to_console('Prepared')
    print_to_console('Saving to file')
    with open(p, 'w') as f:
        f.write('\n'.join(lines))
    return lines


def print_to_console(msg):
    if print_output:
        print_func(msg)


def use(input_count, save_path, write_output=False, show_progress=True, output_count=1):
    global print_output
    print_output = show_progress

    print_to_console(f'Generating table of {input_count} inputs...')
    table = generate_table(input_count, output_count)
    print_to_console(f'Saving table to \'{save_path}\'...')
    table = save_table(save_path, table)
    print_to_console('Saving Done')
    if write_output:
        print('\n'.join(table))


def ask():
    input_count = int(input('Number of inputs in the \'.ttbl\' file: '))
    save_path = input('Path to \'.ttbl\' file to save: ')
    return (input_count, save_path)


if __name__ == '__main__':
    res = ask()
    use(res[0], res[1])
