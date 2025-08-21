import csv
from io import StringIO

def gyms_to_csv(gyms: list[dict]) -> str:
    if not gyms:
        return ""

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=gyms[0].keys())
    writer.writeheader()
    writer.writerows(gyms)
    return output.getvalue()