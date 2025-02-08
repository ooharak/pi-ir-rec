#!/usr/bin/python

import json
import sys

def load_signal(file_path, signal_id):
    # JSONファイルを読み込む
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # 指定された信号IDのデータを取得
    signal = data['signals'].get(str(signal_id))
    if signal is None:
        raise ValueError(f"Signal ID {signal_id} not found.")
    
    return signal

lastvalue=0

def convert_to_delta(signal):
    global lastvalue
    delta_signal = []
    for entry in signal:
        tick = entry['tick']
        level = entry['level']
        dt = tick-lastvalue

        if lastvalue != 0:
          delta_signal.append({'duration': dt, 'kadenkyo': round(dt/425), 'nec':round(dt/562), 'level': level})
        lastvalue=tick
    return delta_signal

def main():
    if len(sys.argv) != 3:
        print("Usage: python decode_ir.py <file_path> <signal_id>")
        sys.exit(1)

    file_path = sys.argv[1]
    signal_id = sys.argv[2]

    try:
        signal = load_signal(file_path, signal_id)
        delta_signal = convert_to_delta(signal)
        #print(json.dumps(delta_signal, indent=1))
        # Output JSONL
        for entry in delta_signal:
          print(json.dumps(entry))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

