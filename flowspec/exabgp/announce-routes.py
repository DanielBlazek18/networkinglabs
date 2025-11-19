#!/usr/bin/env python3

import sys
import time

for item in range(1,20):
    sys.stdout.write(f'announce route 10.0.0.{item}/32 next-hop 191.0.0.2\n')
    sys.stdout.flush()
    time.sleep(.01)

while True:
	time.sleep(60) 
