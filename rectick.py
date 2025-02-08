#!/usr/bin/python

import pigpio
import time
import json
import os

# -------------------------
# 設定パラメータ
# -------------------------
GPIO_PIN = 14         # 使用するGPIOピン番号
TIMEOUT_SECONDS = 0.1 # 信号途絶とみなす時間（秒）
JSON_FILENAME = "ir_signals.json"  # 保存先のJSONファイル

# -------------------------
# グローバル変数
# -------------------------
# 現在記録中の信号（各エッジの情報を格納）
current_signal = []
# 最後に信号があった時刻（信号途絶判定に使用）
last_signal_time = 0

# -------------------------
# JSONファイルの読み込み・保存関数
# -------------------------
def load_data():
    """
    JSONファイルからデータを読み込みます。
    ファイルが存在しない場合は初期状態として作成します。
    """
    if os.path.exists(JSON_FILENAME):
        with open(JSON_FILENAME, "r") as f:
            data = json.load(f)
    else:
        data = {"next_id": 1, "signals": {}}
    return data

def save_data(data):
    """
    データをJSONファイルに保存します。
    """
    with open(JSON_FILENAME, "w") as f:
        json.dump(data, f, indent=4)

last_tick = 0
# -------------------------
# GPIOのコールバック関数
# -------------------------
def callback_func(gpio, level, tick):
    global current_signal, last_signal_time, last_tick
    timestamp = time.time()
    df = tick - last_tick
    last_signal_time = timestamp
    last_tick = tick
    if df < 250:
      return
    # 赤外線受信モジュールは、38kHz 復調済み信号で
    # ON時は 0V（pigpio level==0, "LOW"と記録）、OFF時は 5V（level==1, "HIGH"と記録）となる
    if level == 0:
        level_str = "LOW"
    elif level == 1:
        level_str = "HIGH"
    else:
        # pigpio のコールバックでは level==2 はウォッチドッグタイムアウトなどを示すので無視
        return

    current_signal.append({"tick": tick, "level": level_str})
    print(tick)

# -------------------------
# メイン処理
# -------------------------
def main():
    global current_signal, last_signal_time

    # pigpioライブラリの初期化
    pi = pigpio.pi()
    if not pi.connected:
        print("pigpioデーモンに接続できませんでした。sudo pigpiod を実行してから再試行してください。")
        return

    # GPIOピンの設定
    pi.set_mode(GPIO_PIN, pigpio.INPUT)
    pi.set_glitch_filter(GPIO_PIN, 300)
    
    # GPIO17のエッジ検出（立ち上がり／立ち下がり）のコールバックを設定
    cb = pi.callback(GPIO_PIN, pigpio.EITHER_EDGE, callback_func)

    # JSONデータの読み込み（既存ファイルがあれば内容を使用）
    data = load_data()
    
    try:
        while True:
            time.sleep(0.1)  # ループ間隔。短い間隔で信号途絶の判定を行う。
            if current_signal:
                # 最後の信号から TIMEOUT_SECONDS 以上経過していれば、信号の一区切りと判定
                if time.time() - last_signal_time > TIMEOUT_SECONDS:
                    signal_id = str(data["next_id"])
                    data["signals"][signal_id] = current_signal.copy()
                    data["next_id"] += 1
                    save_data(data)
                    print(f"信号ID {signal_id} を保存しました。イベント数: {len(current_signal)}")
                    # 現在の信号記録をリセットして次の信号の受信を開始
                    current_signal = []
    except KeyboardInterrupt:
        print("終了します...")
    finally:
        cb.cancel()
        pi.stop()

if __name__ == "__main__":
    main()

