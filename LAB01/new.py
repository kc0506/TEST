from datetime import datetime
import time


prev = datetime.now()
time.sleep(0.1)
print((datetime.now() - prev).total_seconds() - 0.0)
