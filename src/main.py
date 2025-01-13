from cmath import log
from datetime import datetime
from scheduling.services.scheduler import ProductionScheduler
from scheduling.utils.data_converter import DataConverter
from scheduling.utils.json_utils import load_json_file
import json
from pathlib import Path

def save_schedule_to_json(schedule, filename="result.json"):
    """Speichert den Zeitplan als JSON-Datei."""
    schedule_data = []
    for item in schedule:
        schedule_data.append({
            "job_name": item.job_name,
            "operation_name": item.operation_name,
            "machine_name": item.machine_name,
            "start_time": item.start_time.strftime('%Y-%m-%d %H:%M'),
            "end_time": item.end_time.strftime('%Y-%m-%d %H:%M')
        })
    
    output_path = Path("output")
    output_path.mkdir(exist_ok=True)
    
    with open(output_path / filename, 'w', encoding='utf-8') as f:
        json.dump(schedule_data, f, indent=4, ensure_ascii=False)

def print_schedule_table(schedule):
    """Gibt den Zeitplan als formatierte Tabelle aus."""
    # Erstelle eine Liste von Listen für die Tabelle
    table_data = []
    for item in schedule:
        table_data.append([
            item.job_name,
            item.operation_name,
            item.machine_name,
            item.start_time.strftime('%Y-%m-%d %H:%M'),
            item.end_time.strftime('%Y-%m-%d %H:%M')
        ])
    
    # Sortiere nach Startzeit
    table_data.sort(key=lambda x: datetime.strptime(x[3], '%Y-%m-%d %H:%M'))
    
    # Definiere die Spaltenüberschriften
    headers = ["Job", "Operation", "Maschine", "Start", "Ende"]
    
    # Bestimme die maximale Breite jeder Spalte
    col_widths = [max(len(str(row[i])) for row in table_data + [headers]) for i in range(len(headers))]
    
    # Erstelle die Trennlinie
    separator = '+' + '+'.join('-' * (width + 2) for width in col_widths) + '+'
    
    # Drucke die Tabelle
    print("\nProduktionszeitplan:")
    print(separator)
    
    # Drucke Header
    header_row = '|'
    for i, header in enumerate(headers):
        header_row += f" {header:{col_widths[i]}} |"
    print(header_row)
    print(separator)
    
    # Drucke Daten
    for row in table_data:
        data_row = '|'
        for i, item in enumerate(row):
            data_row += f" {str(item):{col_widths[i]}} |"
        print(data_row)
    
    print(separator)

def main():
    try:
        # Lade die JSON-Daten
        raw_data = {
            "buffer": load_json_file("buffer.json"),
            "job": load_json_file("job.json"),
            "maschine": load_json_file("maschine.json"),
            "operation": load_json_file("operation.json"),
            "produktionshilfe": load_json_file("produktionshilfe.json"),
            "material": load_json_file("material.json")
        }

        print(json.dumps(raw_data, indent=4))

        # Konvertiere die Daten in Objekte
        jobs = DataConverter.convert_jobs(raw_data["job"])
        machines = DataConverter.convert_machines(raw_data["maschine"])
        operations = DataConverter.convert_operations(raw_data["operation"])
        aids = DataConverter.convert_production_aids(raw_data["produktionshilfe"])
        materials = DataConverter.convert_materials(raw_data["material"])
        buffers = DataConverter.convert_buffers(raw_data["buffer"])

        # Erstelle den Scheduler und generiere den Zeitplan
        scheduler = ProductionScheduler(
            jobs=jobs,
            machines=machines,
            operations=operations,
            aids=aids,
            materials=materials,
            buffers=buffers
        )

        # Generiere den Zeitplan
        schedule = scheduler.create_schedule(datetime.now())

        # Speichere den Zeitplan als JSON
        save_schedule_to_json(schedule)

        # Gib den Zeitplan als Tabelle aus
        print_schedule_table(schedule)

    except Exception as e:
        print(f"Fehler beim Erstellen des Zeitplans: {str(e)}")

if __name__ == "__main__":
    main()
