# TableGeneratorFromLogic.py
import json
import os
from os import path, remove
from os.path import splitext

import pyparsing as pp
from tqdm import tqdm
from yaspin import Spinner, yaspin

import parsers as ps

all_nodes = []
all_input_nodes = []
all_output_nodes = []
tab_count = 4

print_output = True
print_func = print


class NodeStatic:
    @staticmethod
    def _and(x, y):
        if type(x) == bool:
            return bool(x * y)
        elif type(x) == Node:
            return bool(x.state * y.state)
        else:
            raise ValueError('Input data must be \'bool\' or \'Node\' type')

    @staticmethod
    def _or(x, y):
        if type(x) == bool:
            return bool(x + y)
        elif type(x) == Node:
            return bool(x.state + y.state)
        else:
            raise ValueError('Input data must be \'bool\' or \'Node\' type')

    @staticmethod
    def _not(x):
        if type(x) == bool:
            return bool(not x)
        elif type(x) == Node:
            return bool(not x.state)
        else:
            raise ValueError('Input data must be \'bool\' or \'Node\' type')

    @staticmethod
    def _buffer(x):
        if type(x) == bool:
            return bool(x)
        elif type(x) == Node:
            return bool(x.state)
        else:
            raise ValueError('Input data must be \'bool\' or \'Node\' type')

    @staticmethod
    def _nand(x, y):
        if type(x) == bool:
            return bool(not (x * y))
        elif type(x) == Node:
            return bool(not (x.state and y.state))
        else:
            raise ValueError('Input data must be \'bool\' or \'Node\' type')

    @staticmethod
    def _nor(x, y):
        if type(x) == bool:
            return bool(not (x + y))
        elif type(x) == Node:
            return bool(not (x.state or y.state))
        else:
            raise ValueError('Input data must be \'bool\' or \'Node\' type')

    @staticmethod
    def _xor(x, y):
        if type(x) == bool:
            return bool(x * (not y) + (not x) * y)
        elif type(x) == Node:
            return bool(x.state * (not y.state) + (not x.state) * y.state)
        else:
            raise ValueError('Input data must be \'bool\' or \'Node\' type')

    @staticmethod
    def _xnor(x, y):
        if type(x) == bool:
            return bool(x * y + (not x) * (not y))
        elif type(x) == Node:
            return bool(x.state * y.state + (not x.state) * (not y.state))
        else:
            raise ValueError('Input data must be \'bool\' or \'Node\' type')

    @staticmethod
    def _output(x):
        if type(x) == bool:
            return bool(x)
        elif type(x) == Node:
            return bool(x.state)
        else:
            raise ValueError('Input data must be \'bool\' or \'Node\' type')

    @staticmethod
    def _input(x):
        if type(x) == bool:
            return bool(x)
        else:
            raise ValueError('Data must be of type \'bool\'')


class Node:
    def __init__(self, node_type='and', id=0):
        self.type = node_type
        self.id = id
        self.i = []
        self.state = False
        self.run_func = getattr(NodeStatic, '_' + node_type)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.type == other.type and self.id == other.id:
                return True
        return False

    def set_state(self, state=-1):
        if state == -1:
            if self.type == 'input':
                return self.state
            [node.set_state() for node in self.i]
            self.state = self.run_func(*self.i)
            return self.state
        if type(state) == bool:
            self.state = state
            return self.state
        if type(state) == Node:
            self.state = state.state
            return self.state
        raise ValueError('Data must be of type \'bool\' or \'Node\'')

    def __repr__(self, print_other=True, c=0, delete_after=False):
        if print_other:
            if len(self.i) <= 0:
                text = f'{self.type}-{str(self.id)}()'
            elif len(self.i) == 2:
                text = f'{self.type}-{str(self.id)}(\n' + ' ' * ((c + 1) * tab_count) + f'{self.i[0].__repr__(print_other=True, c=c+1)},\n' + ' ' * (
                    (c + 1) * tab_count) + f'{self.i[1].__repr__(print_other=True, c=c+1)})'
            elif len(self.i) == 1:
                text = f'{self.type}-{str(self.id)}(\n' + ' ' * (
                    (c + 1) * tab_count) + f'{self.i[0].__repr__(print_other=True, c=c+1)})'
            else:
                raise Exception('Test error')
        else:
            text = f'{self.type}-{str(self.id)}()'

        if delete_after:
            self.i = None
            self.id = None
            self.type = None

        return text

    def __str__(self):
        return self.__repr__()


def layer_of_nodes_to_str(layer):
    return '[' + ',\n'.join([str(node) for node in layer]) + ']'


def find_inputs_and_outputs():
    for node in all_nodes:
        if node.type == 'input':
            all_input_nodes.append(node)
        elif node.type == 'output':
            all_output_nodes.append(node)

    all_input_nodes.sort(key=lambda o: o.id)
    all_output_nodes.sort(key=lambda o: o.id)
    print(all_input_nodes)


def make_input_table(number=-1):
    if number <= 0:
        number = len(all_input_nodes)
    rows = []
    bin_len = '1' + '0' * number
    for x in range(int(bin_len, 2), int(bin_len, 2) * 2):
        row = []
        rows.append(row)
        nbin = f'{x:b}'[1:]
        for ch in nbin:
            if ch == '0':
                row.append(False)
            else:
                row.append(True)
    return rows


def run_input_table(table):
    full_table = []
    print(table)
    for row in table:
        for idx, inp in enumerate(all_input_nodes):
            inp.set_state(row[idx])
        for idx, out in enumerate(all_output_nodes):
            out.set_state()

        full_table.append((row, [node.state for node in all_output_nodes]))
    return full_table


def replace_from_list_in_str(s, l, replace_with=''):
    for item in l:
        s = s.replace(item, replace_with)
    return s


# def read_json(p):
#     def convert_dict_to_node(_dict):
#         node = Node(node_type=_dict['type'], id=_dict['id'])
#         if node in all_nodes:
#             return all_nodes[all_nodes.index(node)]
#         all_nodes.append(node)
#         for __dict in _dict['i']:
#             node.i.append(convert_dict_to_node(__dict))
#         return node

#     with open(p, 'r') as f:
#         last_layer_bad_format = json.load(f)

#     last_layer = []
#     for _dict in last_layer_bad_format:
#         last_layer.append(convert_dict_to_node(_dict))

#     return last_layer


# def read_logic(p):
#     def convert_list_to_node(_list):
#         if len(_list) == 0:
#             return None
#         node = Node(node_type=_list[0].split(
#             '-')[0].replace(',', ''), id=int(_list[0].split('-')[1]))
#         if node in all_nodes:
#             return all_nodes[all_nodes.index(node)]
#         all_nodes.append(node)
#         for idx in range(0, len(_list[1]), 2):
#             node.i.append(convert_list_to_node(
#                 [_list[1][idx], _list[1][idx + 1]]))
#         return node

#     with open(p, 'r') as f:
#         d = '(' + replace_from_list_in_str(f.read(),
#                                            [' ', '\t', '\n', '\r', '\f', '\v'])[1:-1] + ')'

#     last_layer_bad_format = pp.nestedExpr(
#         opener='(', closer=')', ignoreExpr=None).parseString(d, parseAll=True).asList()[0]
#     last_layer = []
#     for idx in range(0, len(last_layer_bad_format), 2):
#         last_layer.append(convert_list_to_node(
#             [last_layer_bad_format[idx], last_layer_bad_format[idx + 1]]))

#     return last_layer


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
    print_to_console('Saving to file ' + p)
    with open(p, 'w') as f:
        f.write('\n'.join(lines))
    return lines


def print_to_console(msg):
    if print_output:
        print_func(msg)


def use(open_path, save_path, show_output=False, show_progress=True):
    layer = ps.read_logic(open_path, Node) if splitext(open_path)[
        1].lower() == '.logic' else ps.read_json(open_path, Node)
    find_inputs_and_outputs()
    table = make_input_table()
    full_table = run_input_table(table)
    save_table(save_path, full_table)


def ask():
    pass
