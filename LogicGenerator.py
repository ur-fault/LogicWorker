# LogicGenerator.py
from os import path, system
import os
from timeit import Timer
from functools import partial
from tqdm import tqdm
from yaspin import yaspin, Spinner
import json
from sys import getsizeof

print_output = True
print_func = print
tab_count = 4
        

class Node:
    def __init__(self, node_type='and', id=0):
        self.type = node_type.lower()
        self.id = id
        self.i = []

    def __repr__old__(self, print_other=True):
        if print_other:
            if len(self.i) <= 0:
                return f'<Node {self.type} {str(self.id)} []>'
            else:
                return f'<Node {self.type} {str(self.id)} [{self.i[0].__repr__(print_other=False)}, {self.i[1].__repr__(print_other=False)}]>'
        else:
            return f'<Node {self.type} {str(self.id)} []>'

    def __repr__(self, print_other=True, c=0, delete_after=False):
        if print_other:
            if len(self.i) <= 0:
                text = f'{self.type}-{str(self.id)}()'
            elif len(self.i) == 2:
                text = f'{self.type}-{str(self.id)}(\n' + '\t' * ((c + 1) * tab_count) + f'{self.i[0].__repr__(print_other=True, c=c+1)},\n' + '\t' * ((c + 1) * tab_count) + f'{self.i[1].__repr__(print_other=True, c=c+1)})'
            elif len(self.i) == 1:
                text = f'{self.type}-{str(self.id)}(\n' + '\t' * ((c + 1) * tab_count) + f'{self.i[0].__repr__(print_other=True, c=c+1)})'
        else:
            text = f'{self.type}-{str(self.id)}()'
        if delete_after:
            self.i = None
            self.id = None
            self.type = None
        return text

    def __str__(self):
        return self.__repr__()


class Table:
    def __init__(self, p):
        self.i = read_file_i(p)
        self.o = read_file_o(p)
        self.inputs_count = len(read_first_line(p).split(' ')[0].split(','))
        self.lines_count = sum(1 for x in read_file_o(p))
        # print_to_console(self.i)
        # print_to_console(self.o)
        self.i_nodes = self.prep_start_nodes()
        self.trues = self.find_trues_in_output(rm_zeros=True)
        self.negatives = make_not_nodes_for_input(self)

    def prep_start_nodes(self):
        global node_counts
        nodes = []
        
        def run(x):
            nodes.append(Node(node_type='input', id=node_counts['input']))
            node_counts['input'] += 1
        
        # print_to_console(self.i)
        print_to_console('Preparing nodes...')
        if print_output:
            for x in tqdm(range(self.inputs_count)):
                run(x)
        else:
            for x in range(self.inputs_count):
                run(x)
        return nodes

    def find_trues_in_output(self, rm_zeros=False):
        trues_lines = []
        
        def run(idx, inp, out):
            if out == True:
                trues_lines.append((inp, out))
                
        def run2(idx, out):
            if out == False:
                self.i.pop(idx)
                self.o.pop(idx)
        
        print_to_console('Finding true inputs...')
        if print_output:
            for idx, (inp, out) in tqdm(enumerate(zip(self.i, self.o)), total=self.lines_count):
                run(idx, inp, out)
        else:
            for idx, (inp, out) in enumerate(zip(self.i, self.o)):
                run(idx, inp, out)
                
        # if rm_zeros:
        #     print('Removing useless lines...')
        #     if print_output:
        #         for idx, out in tqdm(enumerate(self.o), total=len(self.o)):
        #             run(idx, out)
        #     else:
        #         for idx, out in enumerate(self.o):
        #             run(idx, out)
        
        return trues_lines


node_counts = {'and': 0, 'or': 0, 'input': 0, 'bridge': 0, 'not': 0}


def add_node(node_type):
    global node_counts
    node_counts[node_type] += 1


def make_node_tree_prep(count_of_input, node_type):
    global node_counts
    layer = []
    for x in range(count_of_input):
        layer.append(Node(node_type='bridge', id=node_counts['bridge']))
        node_counts['bridge'] += 1
    return [layer] + make_node_tree(count_of_input, node_type, layer)


def make_node_tree(count_of_trues, node_type, prew_layer=[], prew_prew_layer=[]):
    global node_counts
    if count_of_trues == 1:
        layers = [[Node(node_type=node_type, id=node_counts[node_type])]]
        for prew_node in prew_layer:
            layers[0][0].i.append(prew_node)
        return layers
    elif count_of_trues % 2 == 0:
        nodes = int(count_of_trues / 2)
        # print_to_console(nodes)
        layers = [[]]
        for noden in range(nodes):
            node = Node(node_type=node_type, id=node_counts[node_type])
            node_counts[node_type] += 1
            if len(prew_layer) >= 2:
                node.i.append(prew_layer[noden * 2])
                node.i.append(prew_layer[noden * 2 + 1])
            layers[0].append(node)
        out_count = len(layers[0])
        if len(prew_layer) >= 1:
            if len(prew_layer) % 2 == 1:
                out_count += 1
        if out_count <= 1:
            return layers
        else:
            if len(prew_layer) >= 1:
                if len(prew_layer) % 2 == 1:
                    layers[0].append(prew_layer.pop())
            layers.extend(make_node_tree(out_count, node_type, layers[0], prew_layer))
            return layers
    else:
        nodes = int((count_of_trues - 1) / 2)
        # print_to_console(nodes)
        layers = [[]]
        for noden in range(nodes):
            node = Node(node_type=node_type, id=node_counts[node_type])
            node_counts[node_type] += 1
            if len(prew_layer) >= 2:
                node.i.append(prew_layer[noden * 2])
                node.i.append(prew_layer[noden * 2 + 1])
            layers[0].append(node)
        out_count = len(layers[0]) + 1
        # if len(prew_layer) >= 1:
        #     if len(prew_layer) % 2 == 1:
        #         out_count -= 1
        if out_count <= 1:
            return layers
        else:
            if len(prew_layer) >= 1:
                if len(prew_layer) % 2 == 1:
                    layers[0].append(prew_layer.pop())
            layers.extend(make_node_tree(out_count, node_type, layers[0], prew_layer))
            return layers


def make_condition_nodes(table: Table):
    end_nodes = []
    # print_to_console(table.i_nodes)
    # print_to_console(table.trues)
    def run(idx, combination):
        conditions = []
        for idx2, inp in enumerate(combination):
            if inp:
                conditions.append(table.i_nodes[idx2])
            else:
                conditions.append(table.negatives[idx2])
        and_end_nodes = make_node_tree(len(table.trues[idx][0]), 'and', conditions)[-1][-1]
        end_nodes.append(and_end_nodes)
    
    if print_output:
        for idx, (combination, _) in tqdm(enumerate(table.trues), total=len(table.trues)):
            run(idx, combination)
    else:
        for idx, (combination, _) in enumerate(table.trues):
            run(idx, combination)
    return end_nodes


def make_not_nodes_for_input(table):
    global node_counts
    negatives = []
    print_to_console('Preparing not-nodes for each input')
    
    def run(inp):
        negatives.append(Node(node_type='not', id=node_counts['not']))
        negatives[-1].i = [inp]
        node_counts['not'] += 1
    
    if print_output:
        for inp in tqdm(table.i_nodes):
            run(inp)
    else:
        for inp in table.i_nodes:
            run(inp)
    return negatives


def read_file_i(p):
    with open(p, 'r') as file:
        while True:
            line = file.readline()
            if not line:
                break
            line = line.strip()
            inps, outs = line.split(' ')
            this_inps = []
            for i in inps.split(','):
                if i == '0':
                    this_inps.append(False)
                elif i == '1':
                    this_inps.append(True)
                else:
                    raise Exception('Wrong file')
            yield this_inps
            
def read_file_o(p):
    with open(p, 'r') as file:
        while True:
            line = file.readline()
            if not line:
                break
            out = line.strip().split(' ')[1]
            if out == '0':
                out = False
            elif out == '1':
                out = True
            else:
                raise Exception('Wrong file')
            yield out
            
            
def read_first_line(p):
    with open(p, 'r') as file:
        line = file.readline()
        return line
            


def read_file(p):
    with open(p, 'r') as file:
        lines = file.readlines()
        inp, out = [], []
        
        def run(line):
            line = line.strip()
            inps, outs = line.split(' ')
            this_inps = []
            inp.append(this_inps)
            for i in inps.split(','):
                if i == '0':
                    this_inps.append(False)
                elif i == '1':
                    this_inps.append(True)
                else:
                    raise Exception('Wrong file')
            for o in outs.split(','):
                if o == '0':
                    out.append(False)
                elif o == '1':
                    out.append(True)
                else:
                    raise Exception('Wrong file')
        
        if print_output:
            for line in tqdm(lines):
                run(line)
        else:
            for line in lines:
                run(line)
    # print_to_console(inp, out)
    print_to_console('Reading Done')
    print_to_console('Preparing table object...')
    return Table(inp, out)


def print_to_console(msg):
    if print_output:
        print_func(msg)


def save_to_file(p, data):
    if path.exists(p):
        os.remove(p)
    os.makedirs(path.realpath(path.split(p)[0]), exist_ok=True)
    with open(p, 'w') as f:
        f.write(str(data))
        
def use(table_path, save_path, use_json, write_output = False, tabs=4, print_messages = True):
    global tab_count, print_output
    tab_count = tabs
    print_output = print_messages
    # print(tab_count)
    print_to_console('Reading table file...')
    table = Table(table_path)

    tab_count = 1
    print_to_console('Preparing condition tables...')
    size = getsizeof(table)
    conditions = make_condition_nodes(table)
    table = None
    if print_output:
        print('Deleted \'table\' of size ' + str(size))
    print_to_console('Preparing tree of \'or\' nodes...')
    sp = Spinner(['^-----', '-^----', '--^---', '---^--', '----^-', 
                '-----^', '----^-', '---^--', '--^---', '-^----'], 75)
    if print_output:
        with yaspin(sp, text='Making node tree...', color='green') as spinner:
            res = make_node_tree(len(conditions), 'or', conditions)
            if len(res) > 0:
                if len(res[0]) > 0:
                    end_node = res[-1][0]
                else:
                    end_node = None
            else:
                end_node = None
            spinner.ok('Done')
    else:
        res = make_node_tree(len(conditions), 'or', conditions)
        if len(res) > 0:
            if len(res[0]) > 0:
                end_node = res[-1][0]
            else:
                end_node = None
        else:
            end_node = None
            
    size = getsizeof(conditions)
    conditions = None
    if print_output:
        print('Deleted \'conditions\' of size ' + str(size))
    if use_json:
        if print_output:
            with yaspin(sp, text='Preparing json data to save...', color='green') as spinner:
                if tabs > 0:
                    data = json.dumps(end_node.__dict__, default=lambda o: o.__dict__, indent=tabs)
                else:
                    data = json.dumps(end_node.__dict__, default=lambda o: o.__dict__)
                spinner.ok('Done')
        else:
            if tabs > 0:
                data = json.dumps(end_node.__dict__, default=lambda o: o.__dict__, indent=tabs)
            else:
                data = json.dumps(end_node.__dict__, default=lambda o: o.__dict__)
    else:
        if print_output:
            with yaspin(sp, text='Preparing logic data to save...', color='green') as spinner:
                data = end_node.__repr__(delete_after=True)
                spinner.ok('Done')
        else:
            data = end_node.__repr__(delete_after=True)
    size = getsizeof(end_node)
    end_node = None
    if print_output:
        print('Deleted \'end_node\' of size ' + str(size))
    if print_output:
        with yaspin(sp, text=f'Saving to file \'{save_path}\'...', color='green') as spinner:
            save_to_file(save_path, data)
            spinner.ok('Done')
    else:
        save_to_file(save_path, data)
    print_to_console(f'File saved to \'{save_path}\'')
    if write_output:
        print(data)
        # input('Press any key to continue...')
        
def ask():
    table_path = input('Please input path to truth table: ')
    save_path = input('Please input path to output file: ')
    answer = input('Write output: ').lower()
    answer2 = input('Use \'json\':').lower()
    
    if answer == 'y' or answer == 'yes' or answer == '1':
        write_output = True
    else:
        write_output = False
    if answer2 == 'y' or answer2 == 'yes' or answer2 == '1':
        use_json = True
    else:
        use_json = False
        
    return (table_path, save_path, write_output, use_json)
    

if __name__ == '__main__':
    
    res = ask()
    use(res[0], res[1], res[2], res[3])
    
    # if answer == 'y' or answer == 'yes' or answer == '1':
    #     write_output = True
    # else:
    #     write_output = False
    # if answer2 == 'y' or answer2 == 'yes' or answer2 == '1':
    #     use_json = True
    # else:
    #     use_json = False
        
    # print_to_console('Reading table file...')
    # table = read_file(table_path)

    # tab_count = 1
    # print_to_console('Preparing condition tables...')
    # conditions = make_condition_nodes(table)
    # print_to_console('Preparing tree of \'or\' nodes...')
    # sp = Spinner(['^-----', '-^----', '--^---', '---^--', '----^-', 
    #             '-----^', '----^-', '---^--', '--^---', '-^----'], 75)
    # if print_output:
    #     with yaspin(sp, text='Making node tree...', color='green') as spinner:
    #         res = make_node_tree(len(conditions), 'or', conditions)
    #         if len(res) > 0:
    #             if len(res[0]) > 0:
    #                 end_node = res[-1][0]
    #             else:
    #                 end_node = None
    #         else:
    #             end_node = None
    #         spinner.ok('Done')
    # else:
    #     res = make_node_tree(len(conditions), 'or', conditions)
    #     if len(res) > 0:
    #         if len(res[0]) > 0:
    #             end_node = res[-1][0]
    #         else:
    #             end_node = None
    #     else:
    #         end_node = None
            
    # if use_json:
    #     if print_output:
    #         with yaspin(sp, text='Preparing json data to save...', color='green') as spinner:
    #             data = json.dumps(end_node.__dict__, default=lambda o: o.__dict__, indent=4)
    #             spinner.ok('Done')
    #     else:
    #         data = json.dumps(end_node.__dict__, default=lambda o: o.__dict__, indent=4)
    # else:
    #     data = end_node
        
    # if print_output:
    #     with yaspin(sp, text=f'Saving to file \'{save_path}\'...', color='green') as spinner:
    #         save_to_file(save_path, data)
    #         spinner.ok('Done')
    # else:
    #     save_to_file(save_path, data)
        
    # print_to_console(f'File saved to \'{save_path}\'')
    # if write_output:
    #     print_to_console(end_node)
    #     input('Press any key to continue...')