import traceback
from collector import pull_data_and_alert
try:
    pull_data_and_alert()
except Exception as e:
    traceback.print_exc()