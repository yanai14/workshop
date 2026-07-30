import os
import random

import numpy as np
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser( )
    parser.add_argument('--input_dir',      required=True, help='Path to npys dir')
    parser.add_argument('--parse', action='store_true', default=False)
    parser.add_argument('--split', action='store_true', default=False)
    parser.add_argument("--bin", required=False,type=int,default=7)
    parser.add_argument("--TPS", required=False,type=int,default=60)
    parser.add_argument("--DELTA_T", required=False,type=int,default=60)
    parser.add_argument("--percent",  type=int, default=20, help="split percent")
    parser.add_argument('--out_file_name', required=True)
    args = parser.parse_args()

    if args.parse:
        os.system(f"python .\\generic_parser.py --input {args.input_dir}")

    os.system(f"python .\\process_pipline_filter_csv_with_HAR.py --input_dir {args.input_dir} --output_dir {args.input_dir+"\\filterd_csv"} ")

    os.system(f"python .\\process_pipline_crate_pics.py --input_dir {args.input_dir+"\\filterd_csv"} --bin {args.bin} --TPS {args.TPS} --DELTA_T {args.DELTA_T} --output_dir {args.input_dir+"\\_pics"} ")


    if args.split:
        os.system(f"python .\\process_pipline_unify.py --input_dir {args.input_dir+"\\_pics"} --output_dir {args.input_dir+"\\_unified_pics"} --out_file_name {args.out_file_name} --split --percent {args.percent} ")
    else:
        os.system(f"python .\\process_pipline_unify.py --input_dir {args.input_dir+"\\_pics"} --output_dir {args.input_dir+"\\_unified_pics"} --out_file_name {args.out_file_name}")
