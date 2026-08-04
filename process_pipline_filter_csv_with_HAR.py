import os
import numpy as np
import argparse
import re

def filter_per_conn_for_dir(input_dir,output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(input_dir):
        if not filename.endswith(".csv"):
            continue
        basename = os.path.splitext(filename)[0]
        if "temp" in basename:
            continue
        print(basename)
        filepath_csv = os.path.join(input_dir, basename + '.csv')
        filepath_har = os.path.join(input_dir, basename+'.har')
        if not os.path.exists(filepath_har):
            continue
        print(filepath_har)
        tempout=os.path.join(input_dir, basename+'_temp.csv')
        try:
            os.system(f"python .\\HAR_filter.py --input {filepath_har} --out_name {tempout}")

        except:
            print("failed_har_filter")
            continue

        output_file = os.path.join(output_dir, "filterd_"+basename+".csv")

        try:
            os.system(f"python .\\filter_conn_csv_with_filter_csv.py --input {filepath_csv} --filter_csv {tempout} --out_file {output_file}")
        except:
            print("failed_to_filter_final_csv")

        if os.path.exists(tempout):
            os.remove(tempout)
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='unify npys in dir.'
    )
    parser.add_argument('--input_dir',      required=True,       help='Path to npys dir')
    parser.add_argument('--output_dir', required=True, )
    args = parser.parse_args()
    filter_per_conn_for_dir(
        args.input_dir,
        args.output_dir
    )