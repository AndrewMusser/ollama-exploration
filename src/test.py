from custom_tools import LogTool
import pytz

log_tool = LogTool()

from datetime import datetime

est = pytz.timezone('US/Eastern')

start_time = est.localize(datetime(2024, 9, 3, 0, 0, 0, 0))
end_time = est.localize(datetime(2024, 9, 3, 23, 59, 59, 0))

response = log_tool._run("127.0.0.1", start_time, end_time)

print(response)