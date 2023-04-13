import tomli
import shutil
import os
import argparse
from train import train
from sample import sample
from eval_catboost import train_catboost
from eval_mlp import train_mlp
from eval_simple import train_simple
import pandas as pd
import matplotlib.pyplot as plt
import zero
import lib
import torch

def load_config(path) :
    with open(path, 'rb') as f:
        return tomli.load(f)
    
def save_file(parent_dir, config_path):
    try:
        dst = os.path.join(parent_dir)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.abspath(config_path), dst)
    except shutil.SameFileError:
        pass

def main():
    parser = argparse.ArgumentParser(
                    prog='MLDM',
                    description='Oversampling for multilabel datasets using diffusion models',
                    epilog='If you have any problems, please refer to the documentation')
    parser.add_argument('--config', metavar='FILE')
    parser.add_argument('-d', '--data', default=False)
    parser.add_argument('p', '--oversamplingPercentage',  default=False)
    parser.add_argument('o', '--outputFile', default=False)
    parser.add_argument('--change_val', action='store_true',  default=False)

    args = parser.parse_args()
    raw_config = lib.load_config(args.config)
    if 'device' in raw_config :
        device = torch.device(raw_config['device'])
    else :
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    timer = zero.Timer()
    timer.run()
    save_file(os.path.join(raw_config['parent_dir'], 'config.toml'), args.config)

    train(
        **raw_config['train']['main'],
        **raw_config['diffusion_params'],
        parent_dir=raw_config['parent_dir'],
        real_data_path=raw_config['real_data_path'],
        model_type=raw_config['model_type'],
        model_params=raw_config['model_params'],
        T_dict=raw_config['train']['T'],
        num_numerical_features=raw_config['num_numerical_features'],
        device=device,
        change_val=args.change_val
    )
    sample(
        num_samples=raw_config['sample']['num_samples'],
        batch_size=raw_config['sample']['batch_size'],
        disbalance=raw_config['sample'].get('disbalance', None),
        **raw_config['diffusion_params'],
        parent_dir=raw_config['parent_dir'],
        real_data_path=raw_config['real_data_path'],
        model_path=os.path.join(raw_config['parent_dir'], 'model.pt'),
        model_type=raw_config['model_type'],
        model_params=raw_config['model_params'],
        T_dict=raw_config['train']['T'],
        num_numerical_features=raw_config['num_numerical_features'],
        device=device,
        seed=raw_config['sample'].get('seed', 0),
        change_val=args.change_val
    )

    save_file(os.path.join(raw_config['parent_dir'], 'info.json'), os.path.join(raw_config['real_data_path'], 'info.json'))

    print(f'Elapsed time: {str(timer)}')

if __name__ == '__main__':
    main()