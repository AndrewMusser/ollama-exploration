import xml.etree.ElementTree as ET
from datetime import datetime

def parse_log_file(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Namespace handling
    ns = {'ns': 'http://www.br-automation.com/EventLog'}

    log_entries = []

    # Iterate over EventEntry elements
    for event in root.findall('.//ns:EventEntry', ns):
        entry = {
            'level': event.get('Level'),
            'timestamp': event.get('Time'),
            'error_number': event.get('ErrorNumber'),
            'ascii_data': event.find('ns:ASCII', ns).text if event.find('ns:ASCII', ns) is not None else None
        }
        log_entries.append(entry)

    return log_entries

# Example usage
xml_file = '../data/SystemLogger.logpkg'
logs = parse_log_file(xml_file)

# Print extracted log entries
for log in logs:
    datetime_obj = datetime.strptime(log['timestamp'], "%Y-%m-%dT%H:%M:%S.%f")
    print(datetime_obj)
    print(type(datetime_obj))
    now = datetime.now()
    difference = datetime.now() - datetime_obj
    print(type(difference))