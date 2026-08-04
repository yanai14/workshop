import os
import random

import numpy as np
import argparse
import re

def unify_npy(dir_path,output_dir,out_file):
    os.makedirs(output_dir, exist_ok=True)
    concat_list = []
    for filename in os.listdir(dir_path):
        path = os.path.join(dir_path, filename)

        if os.path.isfile(path) and filename.endswith(".npy"):
            print(path)
            concat_list.append(np.load(path))
    dataset = np.concatenate(concat_list,axis=0)
    np.save(os.path.join(output_dir,out_file), dataset)


def unify_npy_split(dir_path,p,output_dir,out_file):
    os.makedirs(output_dir, exist_ok=True)
    pr=p/100
    concat_list_train = []
    concat_list_test = []
    for filename in os.listdir(dir_path):
        path = os.path.join(dir_path, filename)

        if os.path.isfile(path) and filename.endswith(".npy"):
            print(path)
            array = np.load(path)
            np.random.shuffle(array)

            split_idx = int(len(array) * (1 - pr))

            concat_list_train.extend(array[:split_idx])
            concat_list_test.extend(array[split_idx:])
    print(len(concat_list_train), len(concat_list_test))
    actual_split=len(concat_list_test)/(len(concat_list_train)+len(concat_list_test))
    if actual_split <pr-0.05 or actual_split> pr+0.05:
        if actual_split < pr - 0.05:
            need_to_take=pr-actual_split
            total = len(concat_list_train) + len(concat_list_test)
            n_to_move = round(need_to_take * total)

            random.shuffle(concat_list_train)
            concat_list_test.extend(concat_list_train[:n_to_move])
            concat_list_train = concat_list_train[n_to_move:]
        else:
            need_to_take = -pr + actual_split
            total = len(concat_list_train) + len(concat_list_test)
            print(total)
            n_to_move = round(need_to_take * total)
            random.shuffle(concat_list_test)
            concat_list_train.extend(concat_list_test[:n_to_move])
            concat_list_test = concat_list_test[n_to_move:]

    dataset_train = np.array(concat_list_train)
    dataset_test = np.array(concat_list_test)
    np.save(os.path.join(output_dir,out_file)+"_train", dataset_train)
    np.save(os.path.join(output_dir,out_file) + "_test", dataset_test)





if __name__ == '__main__':
    parser = argparse.ArgumentParser( )
    parser.add_argument('--input_dir',      required=True, help='Path to npys dir')
    parser.add_argument('--split', action='store_true', default=False)
    parser.add_argument("--percent",  type=int, default=20, help="split percent")
    parser.add_argument('--output_dir', required=True)
    parser.add_argument('--out_file_name', required=True)
    args = parser.parse_args()
    if args.split:
        unify_npy_split(
            args.input_dir,
            args.percent,
            args.output_dir,
            args.out_file_name
        )
    else:
        unify_npy(args.input_dir,args.output_dir,args.out_file_name)