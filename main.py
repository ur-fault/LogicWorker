# main.py
import click
import LogicGenerator as lg
import RandomTruthTableGenerator as rttg
import TableGeneratorFromLogic as tgfl
from os.path import splitext


@click.group()
def gens():
    pass


# region fromtabletologic
@gens.command()
@click.argument('input-path', type=click.Path(exists=True), required=True)
@click.argument('output-path', type=click.Path(), required=True)
@click.option('--tab-count', '-t', default=4, help='Count of tabs used in json file.', show_default=True)
@click.option('--show-output/--hide-output', default=False, help='Show logic output.', show_default=True)
@click.option('--show-progress/--hide-progress', default=True, help='Show messages during generation.', show_default=True)
@click.option('--force-file-creation/--do-not-create-empty', default=False, help='LogicGenerator will create logic file even if in table file was no true outputs.', show_default=True)
def fromtabletologic(input_path: str, output_path: str, show_output, show_progress, tab_count, force_file_creation):
    lg.print_func = click.echo
    if splitext(output_path)[1].lower() == '.logic':
        use_json = False
    elif splitext(output_path)[1].lower() == '.json':
        use_json = True
    else:
        click.secho(
            'WARNING: OUTPUT_PATH has unrecognized extension. Automatically setting extension to \'.logic\'', fg='yellow', bold=True)
        output_path += '.logic'
        use_json = False

    lg.use(input_path, output_path, write_output=show_output,
           use_json=use_json, tabs=tab_count, print_messages=show_progress, force_creation=force_file_creation)
# endregion


# region generatetable
@gens.command()
@click.argument('output-path', type=click.Path(), required=True)
@click.argument('input-count', type=click.INT, required=True)
@click.argument('output-count', type=click.INT, required=False, default=1)
@click.option('--show-output/--hide-output', default=False, help='Show table output.', show_default=True)
@click.option('--show-progress/--hide-progress', default=True, help='Show messages during generation.', show_default=True)
def generatetable(output_path, input_count, output_count, show_output, show_progress):
    rttg.print_func = click.echo
    rttg.use(input_count, output_path, write_output=show_output,
             show_progress=show_progress, output_count=output_count)
# endregion    
    

# region fromlogictotable
@gens.command()
@click.argument('input-path', type=click.Path(exists=True), required=True)
@click.argument('output-path', type=click.Path(), required=True)
@click.option('--show-output/--hide-output', default=False, help='Show logic output.', show_default=True)
@click.option('--show-progress/--hide-progress', default=True, help='Show messages during generation.', show_default=True)
def fromlogictotable(input_path, output_path, show_output, show_progress):
    tgfl.print_func = click.echo
    tgfl.use(input_path, output_path, show_output=show_output, show_progress=show_progress)
# endregion


if __name__ == '__main__':
    gens()
