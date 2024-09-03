from custom_tools import LogTool

log_tool = LogTool()

from datetime import datetime

start_time = datetime(2024, 8, 26, 0, 0, 0, 0) 
end_time = datetime(2024, 8, 26, 23, 59, 59, 0)   

response = log_tool._run("127.0.0.1", start_time, end_time)

print(response)