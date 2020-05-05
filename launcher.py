# launcher.py
from os import system, path, chdir, getcwd, listdir, startfile
import click

file_path = path.split(path.realpath(__file__))[0]
cmd = input('>>> ')

# region commands
def check_cmd(cmd, to_check):
    return cmd.lower().split(' ')[0] == to_check.lower()

def clear(cmd):
    click.clear()
    
def cd(cmd):
    if len(cmd.split()) >= 2 and path.isdir(' '.join(cmd.split(' ')[1:])):
        chdir(path.realpath(' '.join(cmd.split()[1:])))
        click.echo('Path changed to ' + getcwd())
    else:
        click.secho('Please provide a valid path', fg='yellow', bold=True)
        
def ls(cmd, maxc=0):
    try:
        if len(cmd.split(' ')) >= 2:
            p = path.realpath(' '.join(cmd.split()[1:]))
            click.echo('Showing content of ' + p)
            content = listdir(p)
        else:
            click.echo('Showing content of ' + getcwd())
            content = listdir(getcwd())
        
        if maxc > 0: 
            if len(content) > maxc:
                content = content[:maxc]
        click.echo('\t' + '\n\t'.join(content))
    except FileNotFoundError as fnfe:
        click.secho('Please provide valid path to a directory', fg='yellow', bold=True)
    except NotADirectoryError as nadr:
        click.secho('Please provide valid path to a directory', fg='yellow', bold=True)
        
            
def reset(cmd):
        chdir(file_path)
        click.echo('The path changed to ' + getcwd())
        
def workdir(cmd):
    click.echo('Current working directory: ' + getcwd())
    
def lsmax(cmd):
    if len(cmd.split(' ')) >= 3:
        num = int(cmd.split(' ')[1])
        p = ' '.join(cmd.split(' ')[2:])
        cmd = 'ls ' + p
        ls(cmd, num)
    elif len(cmd.split(' ')) >= 2:
        num = int(cmd.split(' ')[1])
        p = getcwd()
        cmd = 'ls ' + p
        ls(cmd, num)
    else:
        click.secho('Please provide valid count of items and path', fg='yellow', bold=True)
        
def open(cmd):
    if len(cmd.split(' ')) >= 2:
        p = ' '.join(cmd.split(' ')[1:])
        startfile(p)
        
def help(cmd):
    # print = click.echo
    # prints = click.secho
    click.secho('Launcher for LogicWorker, only for use by user', fg='blue')
    click.echo('Usage: COMMAND [ARGS]')
    click.echo()
    click.echo('Commands:')
    click.echo
    click.echo('\tclear: : clears console')
    click.echo('\tcd: DIR : navigate to directory')
    click.echo('\tls: DIR : list content of directory')
    click.echo('\treset: : navigate back to file directory')
    click.echo('\tworkdir: : prints current working directory')
    click.echo('\tlsmax: MAXCONTENTS DIR : list first MAXCONTENTS item in directory')
    click.echo('\topen: PATHTOFILE : open file in corresponding application')
    click.echo('\thelp | -h: : prints this help message and continue')
    click.echo
    click.echo()
    click.echo('Or you can use normal LogicWorker commands')
 # endregion
    

while cmd.lower() != 'exit':
    try:
        if check_cmd(cmd, 'clear'):
            clear(cmd)
        elif check_cmd(cmd, 'cd'):
            cd(cmd)
        elif check_cmd(cmd, 'ls'):
            ls(cmd)
        elif check_cmd(cmd, 'reset'):
            reset(cmd)
        elif check_cmd(cmd, 'workdir'):
            workdir(cmd)
        elif check_cmd(cmd, 'lsmax'):
            lsmax(cmd)
        elif check_cmd(cmd, 'help') or check_cmd(cmd, '-h'):
            help(cmd)
        elif check_cmd(cmd, 'open'):
            open(cmd)
        else:
            command = f'python "{path.join(file_path, "main.py")}" ' + cmd
            # print(command)
            system(command)
    except KeyboardInterrupt as ki:
        pass
    cmd = input('>>> ')