import csv
import json
from io import StringIO
from typing import List, Dict, Any

# Class: ExportAdapter
class ExportAdapter:
    @staticmethod
    # Method: to_csv
    def to_csv(data: List[Dict[str, Any]]) -> str:
        if not data:
            return ""
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        return output.getvalue()

    @staticmethod
    # Method: to_json
    def to_json(data: List[Dict[str, Any]]) -> str:
        return json.dumps(data, default=str)

    @staticmethod
    # Method: to_excel
    def to_excel(data: List[Dict[str, Any]]) -> str:
        # Placeholder for openpyxl or pandas based generation
        # Returning CSV formatted string as a fallback for the scaffold
        return ExportAdapter.to_csv(data)

    @staticmethod
    # Method: to_pdf
    def to_pdf(data: List[Dict[str, Any]]) -> str:
        # Placeholder for ReportLab or WeasyPrint
        # Returning JSON string as a fallback for the scaffold
        return ExportAdapter.to_json(data)
