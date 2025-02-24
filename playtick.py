#!/usr/bin/python

import sys
import json
import time
import pigpio

# 赤外線LEDを接続したGPIOピン番号
IR_GPIO_PIN = 18  # ハードウェアPWMが可能なGPIOピン

# PWM周波数（38 kHz)
PWM_FREQUENCY = 38_000

# デューティサイクル（例: 1/3）
DUTY_CYCLE = 0.333

T_PER_BURST = 1_000_000/PWM_FREQUENCY
pin = (1 << IR_GPIO_PIN)
#print(f'PIN={pin},ON={int(T_PER_BURST * DUTY_CYCLE)}, OFF={int(T_PER_BURST * (1-DUTY_CYCLE))}')

PWM_ON_DURATION = round(T_PER_BURST * DUTY_CYCLE)
burst = [
  pigpio.pulse(pin, 0, PWM_ON_DURATION),
  pigpio.pulse(0, pin, round(T_PER_BURST - PWM_ON_DURATION))
]

def on_us(us):
  return burst * round(us / T_PER_BURST)

def off_us(us):
  return [pigpio.pulse(0, pin, us)]


def load_ir_signals_from_stdin(pi):
    """標準入力からJSONL形式のdurationを含む赤外線信号データを読み込む"""
    pulses = []
    pulses.extend(off_us(1000))
    for line in sys.stdin:
      entry = json.loads(line)
      duration = entry['duration']
      is_on = True if entry['level'] == 'HIGH' else False
      if is_on:
        pulses.extend(on_us(duration))
      else:
        pulses.extend(off_us(duration))
    pulses.extend(off_us(1000))
    return pulses
      
def send_pulses(pi, pulses):
  waves = []
  for i in range(0, len(pulses), 5000):
    chunk = pulses[i:i+5000]
    pi.wave_add_generic(chunk)
    wave = pi.wave_create()
    if wave < 0:
      raise RuntimeError(f'failed to create a wave #{i}')
    waves.append(wave)
  chain = []
  for wave in waves:
    chain.extend([255, 0, wave])
  pi.wave_chain(chain)
  while pi.wave_tx_busy():
    time.sleep(0.01)
  for wave in waves:
    pi.wave_delete(wave)

def main():
    
    # pigpioに接続
    pi = pigpio.pi()
    if not pi.connected:
        print("pigpioに接続できませんでした。")
        return
    pi.set_mode(IR_GPIO_PIN, pigpio.OUTPUT)
    pi.wave_clear()

    # 赤外線信号データを読み込む
    pulses = load_ir_signals_from_stdin(pi)
    send_pulses(pi, pulses)

    # pigpioから切断
    pi.stop()

if __name__ == '__main__':
    main()

