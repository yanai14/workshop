#!/usr/bin/env python


import csv
import argparse
import os
import sys
import pandas as pd




def matches_filter(row,filter_csv_pd):
    """Return True if row matches all provided (non-None) filter values."""


    for _, row_filter in filter_csv_pd.iterrows():
        checks = [
            (row_filter[0],   row[1]),#src ip
            (row_filter[1], row[2]),#src port
            (row_filter[2],   row[3]),#dest ip
            (row_filter[3], row[4]),#dest port
            (row_filter[4],    row[5]),#protocol
        ]
        if all(pd.isna(fval) or fval == rval for fval, rval in checks):
            return True
    return False


def rewrite_sessions(csv_path,filter_csv_pd,out_file):
    matches = []

    with open(csv_path, "r", newline="") as infile, \
            open(out_file, "w", newline="") as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        for row in reader:
            if len(row) < 9:
                continue

            if not matches_filter(row, filter_csv_pd):
                continue

            writer.writerow(row)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='2D histogram for sessions matching a 5-tuple filter.'
    )
    parser.add_argument('--input',      required=True,       help='Path to CSV file')
    parser.add_argument('--filter_csv', required=False, help='Path to filer CSV file data =src_ip, src_port, dst_ip, dst_port, proto')
    parser.add_argument('--out_file', required=True, help='output npy file name')


    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: file not found: {args.input}")
        sys.exit(1)

    filter_df = pd.read_csv(args.filter_csv, header=None)
    filter_df=filter_df.where(pd.notna(filter_df), None)
    rewrite_sessions(
        csv_path= args.input,
        filter_csv_pd=filter_df,
        out_file = args.out_file
    )
