import os
import logging
from collections import OrderedDict
from datetime import datetime

import click
import pandas as pd
from kami.Kami import Kami
from rich.progress import Progress

from src.bin import parsing_xml, get_workers

@click.command()
@click.argument('model', type=str)
@click.option("-d", "--datadir", "datadir", type=click.Path(exists=True, dir_okay=True, file_okay=False),
              default="data_test/", help="folder containing test files (xml, images)")
@click.option("-t", "--transforms", "transforms",default="XP",
              help="""Allows you to apply transforms to the text. 
                        D : Deletes all digits and numbers;
                        U : Shift the text;
                        L : Minusculise the text;
                        P : Delete punctuation;
                        X : Deletes diacritical marks;""")
@click.option("-v", "--verbosity", "verbose", is_flag=True,
              help="Allows you to retrieve execution logs to follow the process. False by default")
@click.option("-tr", "--truncate", "truncate",default=True,
              help="Option to use to truncate the final result. True by default")
@click.option("-p", "--percent", "percent",default=True,
              help="Option to display a result in percent. True by default")
@click.option("-r", "--round", "round_digits", default='0.01',
              help="Option to set the digits after the decimal point. 0.01 by default")
def test_model(model, **kwargs):

    current_path = os.getcwd()
    model_path = os.path.join(current_path, model)
    output_path = os.path.join(current_path, 'output')

    # Output path
    if not os.path.exists(output_path):
        logging.info(
            f"Dir creation output_path: {str(model_path)}", exc_info=True)
        if kwargs['verbose']:
            click.echo(f"An error has occurred : the HTR model can be found along the following path : {str(model_path)}")
        os.makedirs(output_path)

    # Check model
    if not os.path.exists(model_path):
        logging.error(f"An error has occurred : the HTR model can be found along the following path : {str(model_path)}", exc_info=True)
        if kwargs['verbose']:
            click.echo(f"An error has occurred : the HTR model can be found along the following path : {str(model_path)}")
        click.echo(f"program exit ...")
        exit()

    # check workers cpu
    workers = get_workers()

    # init dataframe
    dict_df = {
        'all_transforms': None,
        'default': None,
        'remove_diacritics': None,
        'remove_punctuation': None,
        'lowercase': None,
        'non_digits': None,
        'uppercase': None
    }

    # get files and test them
    list_files = parsing_xml(kwargs['datadir'])
    with Progress() as progress:
        task = progress.add_task("[cyan]Processing files...", total=len(list_files))
        task_2 = progress.add_task("[red]Saving dataframe...", total=len(dict_df))

        for n, (xml_path, image_path) in enumerate(list_files):
            try:
                kevaluator = Kami(xml_path,
                              model=model_path,
                              image=image_path,
                              workers=workers,
                              apply_transforms=kwargs['transforms'],
                              verbosity=kwargs['verbose'],
                              truncate=kwargs['truncate'],
                              percent=kwargs['percent'],
                              round_digits=kwargs['round_digits'])


                result = kevaluator.scores.board

                # get filename
                filename = os.path.basename(xml_path)

                # build df on score board :
                # 'all_transforms', 'default', 'remove_diacritics', 'remove_punctuation', 'lowercase', 'non_digits', 'uppercase'
                for k in result:
                    ordered_dict = OrderedDict([('filename', filename)] + list(result[k].items()))
                    try:
                        if dict_df[k] is None:
                            dict_df[k] = pd.DataFrame.from_dict([ordered_dict])
                        else:
                            dict_df[k].loc[n] = ordered_dict
                    except KeyError:
                        pass

            except Exception as err:
                logging.error(
                    f"impossible to evaluate the following file : {str(xml_path)} because  error {str(err)}", exc_info=True)
                if kwargs['verbose']:
                    click.echo(
                        f"impossible to evaluate the following file : {str(xml_path)} because  error {str(err)}")
                pass
            progress.update(task, advance=1)

    # metadata
    metadatas = {}

    now = datetime.now()
    metadatas['DATETIME'] = now.strftime("%d_%m_%Y_%H:%M")
    metadatas['MODEL'] = os.path.basename(model_path).split('.')[0]

    for k, df in dict_df.items():
        metadatas['TRANSFORM'] = k
        name_csv = f"evaluation_report_kami_{metadatas['DATETIME']}_{metadatas['MODEL']}_{metadatas['TRANSFORM']}.csv"
        if df is not None:
            df.to_csv(os.path.join(output_path, name_csv), mode='w+', header=True)
        progress.update(task_2, advance=1)


if __name__ == '__main__':
    logging.basicConfig(filename='logfile.txt', level=logging.WARNING,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    test_model()
