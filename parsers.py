# parsers.py
import pyparsing as pp
import json
from os import path
import os


# region read files


def read_logic(p, cls):
    def replace_from_list_in_str(s, l, replace_with=''):
        for item in l:
            s = s.replace(item, replace_with)
        return s

    def convert_list_to_node(_list):
        if len(_list) == 0:
            return None
        node = Node(node_type=_list[0].split(
            '-')[0].replace(',', ''), id=int(_list[0].split('-')[1]))
        if node in all_nodes:
            return all_nodes[all_nodes.index(node)]
        all_nodes.append(node)
        for idx in range(0, len(_list[1]), 2):
            node.i.append(convert_list_to_node(
                [_list[1][idx], _list[1][idx + 1]]))
        return node

    Node = cls
    all_nodes = []

    with open(p, 'r') as f:
        d = '(' + replace_from_list_in_str(f.read(),
                                           [' ', '\t', '\n', '\r', '\f', '\v'])[1:-1] + ')'

    last_layer_bad_format = pp.nestedExpr(
        opener='(', closer=')', ignoreExpr=None).parseString(d, parseAll=True).asList()[0]
    last_layer = []
    for idx in range(0, len(last_layer_bad_format), 2):
        last_layer.append(convert_list_to_node(
            [last_layer_bad_format[idx], last_layer_bad_format[idx + 1]]))

    return (last_layer, all_nodes)


def read_json(p, cls):
    def convert_dict_to_node(_dict):
        node = Node(node_type=_dict['type'], id=_dict['id'])
        if node in all_nodes:
            return all_nodes[all_nodes.index(node)]
        all_nodes.append(node)
        for __dict in _dict['i']:
            node.i.append(convert_dict_to_node(__dict))
        return node

    Node = cls
    all_nodes = []

    with open(p, 'r') as f:
        last_layer_bad_format = json.load(f)

    last_layer = []
    # print(last_layer_bad_format)
    for _dict in last_layer_bad_format:
        last_layer.append(convert_dict_to_node(_dict))

    return (last_layer, all_nodes)
# endregion
# region write files


def save_json(p, layer, tabs=4):
    def save_to_file(data):
        if path.exists(p):
            os.remove(p)
        os.makedirs(path.realpath(path.split(p)[0]), exist_ok=True)
        with open(p, 'w') as f:
            f.write(str(data))
    data = json.dumps(layer, default=lambda o: o.__dict__, indent=tabs)
    save_to_file(data=data)


def save_logic(p, layer):
    def save_to_file(data):
        if path.exists(p):
            os.remove(p)
        os.makedirs(path.realpath(path.split(p)[0]), exist_ok=True)
        with open(p, 'w') as f:
            f.write(str(data))
    data = '[' + ',\n'.join([str(node) for node in layer]) + ']'
    save_to_file(data=data)
# endregion
