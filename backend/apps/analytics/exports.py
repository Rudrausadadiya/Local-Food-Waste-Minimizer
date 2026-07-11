import csv
import json
from io import StringIO
from typing import List, Dict, Any

class ExportAdapter:
    @staticmethod
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
    def to_json(data: List[Dict[str, Any]]) -> str:
        return json.dumps(data, default=str)

    @staticmethod
    def to_excel(data: List[Dict[str, Any]]) -> str:
        # Placeholder for openpyxl or pandas based generation
        # Returning CSV formatted string as a fallback for the scaffold
        return ExportAdapter.to_csv(data)

    @staticmethod
    def to_pdf(data: List[Dict[str, Any]]) -> str:
        # Placeholder for ReportLab or WeasyPrint
        # Returning JSON string as a fallback for the scaffold
        return ExportAdapter.to_json(data)
