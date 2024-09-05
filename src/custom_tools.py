from typing import Optional, Type
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from datetime import datetime
import xml.etree.ElementTree as ET
import subprocess
import pytz
import os.path

class LogInput(BaseModel):
    ip: str = Field(description="IP address of the machine")
    start_date: datetime = Field(description="Offset-aware start date and time for the desired log messages, in the EST timezone, in ISO format")
    end_date: datetime = Field(description="Offset-aware end date and time for the desired log messages, in the EST timezone, in ISO format")

class LogTool(BaseTool):
    name = "LogTool"
    description = """
        Useful for retrieving the logs from a machine, and finding out what happened on the machine.
        You specify the IP address of the machine as an input, and a start and end date, and the tool returns a list of log messages that occurred betwen those dates.
        If you don't know the IP, you should assume that it is 127.0.0.1
    """
    args_schema: Type[BaseModel] = LogInput
    return_direct: bool = False

    def _run(
        self, ip: str, start_date: datetime, end_date: datetime, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        # Convert to offset-aware if needed.
        est = pytz.timezone('US/Eastern')
        if start_date.tzinfo is None:
            start_date = est.localize(start_date)
        if end_date.tzinfo is None:
            end_date = est.localize(end_date)
        # Now get to work retrieving the log file, reading it, and searching it.
        log_file_path = self._retrieve_log_file(ip)
        log_messages = self._get_log_messages(log_file_path)
        filtered_log_messages = self._filter_log_messages(log_messages, start_date, end_date)
        serialized_messages = self._serialize_log_messages(filtered_log_messages)
        if (serialized_messages != ''):
            return serialized_messages
        else:
            return 'There are no messages in this date range' 

    async def _arun(
        self,
        ip: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Log tool does not support async")

    def _retrieve_log_file(self, ip):
    
        pvi_transfer_path = "C:\BRAutomation\PVI\V4.12\PVI\Tools\PVITransfer\PVITransfer.exe"
        pil_file_path = "..\data\get_logger.pil"
        logger_file_path = "..\data\SystemLogger.logpkg"
        # If the log file already exists, skip the next step of querying it, and just return its name.
        if os.path.isfile("..\data\SystemLogger.logpkg"):
            return logger_file_path
        else:
            with open(pil_file_path, 'w+') as f:
                f.write(f'Connection "/IF=TCPIP /SA=1", "/DA=2 /DAIP={ip} /REPO=11160", "WT=30"\n')
                f.write('LoadSystemInformationForLogger\n')
                f.write('LoadTextModulesForLogger\n')
                f.write(f'Logger "System", "$arlogsys", ".logpkg", "{logger_file_path}", "en"')

            cmd = []
            cmd.append(pvi_transfer_path)
            cmd.append('-silent')
            cmd.append(pil_file_path)
            process = subprocess.run(cmd)      
            if process.returncode == 0:
                return logger_file_path
            else:
                return ''
                # Handle the error somehow   

    def _retrieve_text(self, texts, id):
        for text in texts:
            if text['id'] == id:
                return text['text']
        return ''

    def _get_log_messages(self, xml_file):
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Namespace handling
        ns = {'ns': 'http://www.br-automation.com/EventLog'}

        # Iterate over Text elements
        texts = []
        for text in root.findall('.//ns:Text', ns):
            text = {
                'id': text.get('Id'),
                'text': text.text
            }
            texts.append(text)
        
        log_entries = []
        # Iterate over EventEntry elements
        for event in root.findall('.//ns:EventEntry', ns):
            utc = pytz.utc
            est = pytz.timezone('US/Eastern')
            utc_timestamp = utc.localize(datetime.strptime(event.get('Time'), "%Y-%m-%dT%H:%M:%S.%f"))
            est_timestamp = utc_timestamp.astimezone(est)
            entry = {
                'level': event.get('Level'),
                'timestamp': est_timestamp,
                'error_number': event.get('ErrorNumber'),
                'ascii_data': event.find('ns:ASCII', ns).text if event.find('ns:ASCII', ns) is not None else '',
                'text': self._retrieve_text(texts, event.get('TextId'))
            }
            log_entries.append(entry)

        return log_entries

    def _filter_log_messages(self, messages, start_date, end_date):
        filtered_log_messages = []
        for message in messages:
            if start_date <= message['timestamp'] <= end_date:
                filtered_log_messages.append(message)
        return filtered_log_messages

    def _serialize_log_messages(self, messages):
        serialized_messages = ''
        for message in messages:
            if (message['ascii_data'] != ''):
                serialized_message = str(message['timestamp']) + ' | ' + message['level'] + ' | ' + message['error_number'] + ' | ' + message['ascii_data'] + ' - ' + message['text']
            else:
                serialized_message = str(message['timestamp']) + ' | ' + message['level'] + ' | ' + message['error_number'] + ' | ' + message['text']
            serialized_messages = serialized_messages + serialized_message + '\n'
        return serialized_messages
    
class DateTimeTool():

    def retrieve_date_and_time(self):
        now = datetime.datetime.now()
        # Format the date as "Friday, the 13th of August, 2024"
        date_str = now.strftime("%A, the %d")
        # Add the ordinal suffix (st, nd, rd, th)
        day = now.day
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]
        date_str += f"{suffix} of %B, %Y"
        # Format the time as "21:04:44"
        time_str = now.strftime("%H:%M:%S")
        return date_str, time_str