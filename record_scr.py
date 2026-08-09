import os
import argparse
import subprocess
import time


def rec(PythonScript, CaptureName, output_dir, Count):
        os.makedirs(output_dir, exist_ok=True)

        for i in range(Count):
            try:
                proc = subprocess.Popen([r"C:\Program Files\Wireshark\dumpcap.exe", "-i", "Wi-Fi","-F","pcap","-p","-w",output_dir+f"\\{CaptureName}_{i}.pcap"],
                                            stdout=subprocess.DEVNULL,
                                            stderr=subprocess.DEVNULL)
            except Exception as e:
                print("dumpcap problem")
                proc.terminate()
                proc.wait()
            time.sleep(1)
            try:
                os.system(f"python {PythonScript} --output_name {output_dir}\\{CaptureName}_{i}.har")
            except Exception as e:
                print("playwright script problem")
                proc.terminate()
                proc.wait()
            proc.terminate()
            proc.wait()
            print("Done")

if __name__ == '__main__':
    parser = argparse.ArgumentParser( )
    parser.add_argument('--PythonScript',  required=True)
    parser.add_argument("--Count", required=True,type=int)
    parser.add_argument("--CaptureName", required=True)
    parser.add_argument("--output_dir", required=True)

    args = parser.parse_args()

    rec(args.PythonScript, args.CaptureName, args.output_dir, args.Count)