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

class LogInput(BaseModel):
    ip: str = Field(description="IP address of the machine")
    start_date: datetime = Field(description="The start date and time for the desired log messages")
    end_date: datetime = Field(description="The end date and time for the desired log messages")

class LogTool(BaseTool):
    name = "LogTool"
    description = "useful for retrieving the logs from a machine. You specify the IP address of the machine as an input, and a start and end date, and the tool returns a list of log messages that occurred betwen those dates. If you don't know the IP, you should assume that it is 127.0.0.1"
    args_schema: Type[BaseModel] = LogInput
    return_direct: bool = False

    def _run(
        self, ip: str, start_date: datetime, end_date: datetime, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        # Convert offset-aware time to offset-naive.
        if start_date.tzinfo is not None:
            start_date = start_date.astimezone(tz=None).replace(tzinfo=None)
        if end_date.tzinfo is not None:
            end_date = end_date.astimezone(tz=None).replace(tzinfo=None)
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
            entry = {
                'level': event.get('Level'),
                'timestamp': datetime.strptime(event.get('Time'), "%Y-%m-%dT%H:%M:%S.%f"),
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