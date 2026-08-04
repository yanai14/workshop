import os
import numpy as np
import argparse
import re

def pics_per_conn(input_dir,bin,TPS,DELTA_T,output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(input_dir):
        if not filename.endswith(".csv"):
            continue
        basename= os.path.splitext(filename)[0]
        filepath_csv = os.path.join(input_dir, filename)
        try:
            os.system(f"python .\\box_pics_array_crator_sparte.py --input {filepath_csv} --bin {bin} --TPS {TPS} --DELTA_T {DELTA_T} --out_file {os.path.join(output_dir, basename+"_")}")
        except:
            print("failed pics_array_crator")
            continue



if __name__ == '__main__':
    parser = argparse.ArgumentParser( )
    parser.add_argument('--input_dir',      required=True,       help='Path to npys dir')
    parser.add_argument("--bin", required=False,type=int,default=5)
    parser.add_argument("--TPS", required=False,type=int,default=60)
    parser.add_argument("--DELTA_T", required=False,type=int,default=60)
    parser.add_argument('--output_dir', required=True, )
    args = parser.parse_args()
    pics_per_conn(
        args.input_dir,
        args.bin,
        args.TPS,
        args.DELTA_T,
        args.output_dir
    )