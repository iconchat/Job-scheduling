from datetime import datetime
from typing import Dict, List, Any
from ..models.entities import Job, Machine, Operation, ProductionAid, Material, Buffer

class DataConverter:
    @staticmethod
    def convert_jobs(data: List[Dict[str, Any]]) -> List[Job]:
        return [
            Job(
                name=item['Name'],
                deadline=datetime.strptime(item['Lieferfrist'], '%Y-%m-%d'),
                priority=item['Priorität'],
                earliest_start=datetime.strptime(item['frühesterStarttermin'], '%Y-%m-%d'),
                required_quantity=item['benötigteEndproduktmenge']
            )
            for item in data
        ]

    @staticmethod
    def convert_machines(data: List[Dict[str, Any]]) -> List[Machine]:
        return [
            Machine(
                name=item['Name'],
                maintenance_time=item['Wartungszeit'],
                maintenance_account=item['Wartungszeitkonto'],
                production_frequencies=item['fertigungsfrequenz'],
                cost_per_time_unit=item['KostenProZeiteinheit']
            )
            for item in data
        ]

    @staticmethod
    def convert_operations(data: List[Dict[str, Any]]) -> List[Operation]:
        return [
            Operation(
                name=item['Name'],
                material_quantity=item['Materialmenge'],
                min_storage_time=item['Mindestlagerzeit'],
                required_time=item['benötigteZeit'],
                simultaneous_production=item['gleichzeitigeProduktion'],
                predecessors=item['Predecessor'],
                required_aids_count=item['nötigeProduktionshilfenanzahl'],
                cost_per_time_unit=item['KostenProZeiteinheit'],
                output_quantity=item['OutputMenge']
            )
            for item in data
        ]

    @staticmethod
    def convert_production_aids(data: List[Dict[str, Any]]) -> List[ProductionAid]:
        return [
            ProductionAid(
                name=item['Name'],
                type=item['Typ'],
                available_quantity=item['VerfügbareMenge'],
                cost=item['Kosten']
            )
            for item in data
        ]

    @staticmethod
    def convert_materials(data: List[Dict[str, Any]]) -> List[Material]:
        return [
            Material(
                name=item['Name'],
                delivery_time=item['materialspezifischeAnlieferzeit'],
                cost=item['Kosten']
            )
            for item in data
        ]

    @staticmethod
    def convert_buffers(data: List[Dict[str, Any]]) -> List[Buffer]:
        return [
            Buffer(
                machine_name=item['Maschinenname'],
                duration=item['Dauer'],
                cost=item['Kosten']
            )
            for item in data
        ]
