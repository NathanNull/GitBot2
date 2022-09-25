import time
import sys

print("hey")
for i in range(1000000):
    time.sleep(2)
    print("hey")
    if i%5 == 0:
        sys.stdout.flush()