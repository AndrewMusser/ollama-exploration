from datetime import datetime
import xml.etree.ElementTree as ET
import subprocess
import pytz
import os.path

class LogTool():

    def run(self, ip: str) -> str:
        # Get to work retrieving the log file, reading it, and searching it.
        log_file_path = self._retrieve_log_file(ip)
        log_messages = self._get_log_messages(log_file_path)
        serialized_messages = self._serialize_log_messages(log_messages)
        if (serialized_messages != ''):
            return serialized_messages
        else:
            return 'There are no log messages' 

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
        now = datetime.now()
        # Format the date as "Friday, the 13th of August, 2024"
        date_str = now.strftime("%A, the %d")
        # Add the ordinal suffix (st, nd, rd, th)
        day = now.day
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]
        date_str += f"{suffix} of {now.strftime('%B, %Y')}"
        # Format the time as "21:04:44"
        time_str = now.strftime("%H:%M:%S")
        return date_str, time_str