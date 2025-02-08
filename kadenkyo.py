#!/usr/bin/python

import sys
import json

# dec_tick.py json num | kadenkyo.py


def generate_from_stdin():
  for line in sys.stdin:
    line = line.strip()
    entry = json.loads(line)
    yield entry
    #kadenkyo = entry['kadenkyo']
    #level = entry['level']
    #yield kadenkyo, level


def do_assert(entry, kadenkyo, level, desc):
  if entry['kadenkyo']==kadenkyo and entry['level']==level:
    pass
  else:
    raise f'format error: {desc}: expected: {kadenkyo},{level}; actual: {json.dumps(entry)}'


def parse_bits(gen, length, desc):
  value = 0
  for n in range(0,length):
    do_assert(next(gen), 1, 'HIGH', f'{desc} Bit #{n}')
    entry = next(gen)
    kadenkyo = entry['kadenkyo']
    level = entry['level']
    if kadenkyo not in [1,3] or level != 'LOW':
      raise f'format error: {desc} bit #{n}: actual: {json.dumps(entry)}'
    value = (value >> 1) | (0x80 if kadenkyo == 3 else 0)
  return value


# phases: L(eader), C(ustomer Code), D(ata)
def parse():
  phase = 'L'
  gen = generate_from_stdin()
  do_assert(next(gen), 8, 'HIGH', 'Frame Leader H')
  do_assert(next(gen), 4, 'LOW', 'Frame Leader L')
  cc1 = parse_bits(gen, 8, 'Customer Code first')
  cc2 = parse_bits(gen, 8, 'Customer Code second')
  par = parse_bits(gen, 4, 'Parity')
  d0 = parse_bits(gen, 4, 'Data #0')
  d1 = parse_bits(gen, 8, 'Data #1')
  d2 = parse_bits(gen, 8, 'Data #2')
  d3 = parse_bits(gen, 8, 'Data #3')
  
  print('{:02x}'.format(cc1), end=' ')
  print('{:02x}'.format(cc2), end=' ')
  #print('{:02x}'.format(par), end=' ')
  print('{:02x}'.format(d0), end=' ')
  print('{:02x}'.format(d1), end=' ')
  print('{:02x}'.format(d2), end=' ')
  print('{:02x}'.format(d3), end=' ')
  
parse()
