#!/usr/bin/env python


import csv
import argparse
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from numpy.ma.core import append

MTU=1500
BMU=1500






def plot_sessions(csv_path,bins,TPS,DELTA_T,out_file):
    num_conn=0
    with open(csv_path, "r", encoding="utf-8") as f:
        num_conn = sum(1 for line in f)

    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if len(row) < 9:
                continue

            try:
                length = int(row[7])
            except ValueError:
                continue

            if length < 2:
                continue

            ts = np.array(row[8:8+length], dtype=float)
            sizes = np.array(row[9+length:], dtype=int)

            if len(ts) == 0 or len(sizes) == 0:
                continue

            print(csv_path,(i/num_conn)*100,"%")
            conn_dataset=[]

            for t in range(max(int(ts[-1] / DELTA_T - TPS / DELTA_T),0)+1):#changed from original need at least 60 sec
                mask = ((ts >= t * DELTA_T) & (ts <= (t * DELTA_T + TPS)))
                # print t * DELTA_T, t * DELTA_T + TPS, ts[-1]
                ts_mask = ts[mask]
                sizes_mask = sizes[mask]


                if len(ts_mask) > 10:
                    tps = TPS
                    if tps is None:
                        max_delta_time = ts_mask[-1] - ts_mask[0]

                    else:
                        max_delta_time = tps

                    bin_len = bins

                    ts_norm = ((np.array(ts_mask) - ts_mask[0]) / max_delta_time) * MTU
                    H, xedges, yedges = np.histogram2d(
                        ts_norm,
                        sizes_mask,
                        bins=(
                            range(0, MTU + 1, bin_len),
                            range(0, BMU + 1, bin_len)
                        )
                    )

                    #H = (H > 0).astype(np.uint16)
                    if False:
                        fig, ax = plt.subplots(figsize=(7, 7))

                        im = ax.pcolormesh(
                            xedges,  # X edges
                            yedges,  # Y edges
                            H.T,  # transpose because histogram2d stores x first
                            cmap='hot_r',
                            shading='auto'
                        )

                        plt.show()

                        plt.close()
                    conn_dataset.append(H.T)
            if len(conn_dataset)!=0:
                conn_dataset = np.array(conn_dataset)

                np.save( out_file+str(i), conn_dataset)
                print(out_file+str(i)+" is done")








if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='2D histogram for sessions matching a 5-tuple filter.'
    )
    parser.add_argument('--input',      required=True,       help='Path to CSV file')
    parser.add_argument("--bin", required=False,type=int,default=5)
    parser.add_argument("--TPS", required=False,type=int,default=60)
    parser.add_argument("--DELTA_T", required=False,type=int,default=60)
    parser.add_argument('--out_file', required=True, help='output npy file name')


    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: file not found: {args.input}")
        sys.exit(1)

    plot_sessions(
        csv_path= args.input,
        bins=args.bin,
        TPS=args.TPS,
        DELTA_T=args.DELTA_T,
        out_file = args.out_file
    )
