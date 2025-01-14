from datetime import datetime, timedelta
from typing import List, Dict, Optional
from ..models.entities import Job, Machine, Operation, ProductionAid, Material, Buffer
from dataclasses import dataclass

@dataclass
class SchedulingResult:
    """
    Repräsentiert das Ergebnis einer geplanten Operation im Produktionsplan.
    Enthält alle relevanten Informationen über einen einzelnen Produktionsschritt.
    """
    job_name: str          # Name des übergeordneten Auftrags
    operation_name: str    # Name der durchzuführenden Operation
    machine_name: str      # Name der verwendeten Maschine
    start_time: datetime   # Startzeit der Operation
    end_time: datetime     # Endzeit der Operation
    resources_used: Dict[str, int]  # Verwendete Ressourcen und ihre Mengen

class MachineScheduler:
    """
    Verwaltet die Maschinenbelegung und Zeitplanung.
    Stellt sicher, dass keine Überschneidungen in der Maschinenbenutzung auftreten.
    """
    def __init__(self):
        # Liste aller geplanten Operationen
        self.scheduled_operations: List[SchedulingResult] = []
        # Speichert für jede Maschine ihre Belegungszeiten als Liste von (start, end) Tupeln
        self.machine_availability: Dict[str, List[tuple]] = {}
        # Speichert die Ressourcennutzung über die Zeit
        self.resource_usage: Dict[str, Dict[datetime, int]] = {}

    def is_machine_available(self, machine_name: str, start_time: datetime, duration: int) -> bool:
        """
        Überprüft, ob eine Maschine zu einem bestimmten Zeitpunkt verfügbar ist.
        
        Args:
            machine_name: Name der zu überprüfenden Maschine
            start_time: Gewünschte Startzeit
            duration: Benötigte Dauer in Minuten
        
        Returns:
            True wenn die Maschine im gewünschten Zeitraum verfügbar ist, sonst False
        """
        if machine_name not in self.machine_availability:
            return True  # Maschine wurde noch nie benutzt, also ist sie verfügbar
        
        end_time = start_time + timedelta(minutes=duration)
        # Prüfe alle existierenden Buchungen der Maschine
        for busy_start, busy_end in self.machine_availability[machine_name]:
            # Wenn sich die Zeiträume überschneiden, ist die Maschine nicht verfügbar
            if not (end_time <= busy_start or start_time >= busy_end):
                return False
        return True

    def reserve_machine(self, machine_name: str, start_time: datetime, duration: int):
        """
        Reserviert eine Maschine für einen bestimmten Zeitraum.
        
        Args:
            machine_name: Name der zu reservierenden Maschine
            start_time: Startzeit der Reservierung
            duration: Dauer der Reservierung in Minuten
        """
        end_time = start_time + timedelta(minutes=duration)
        if machine_name not in self.machine_availability:
            self.machine_availability[machine_name] = []
        # Füge neue Reservierung hinzu und sortiere nach Startzeit
        self.machine_availability[machine_name].append((start_time, end_time))
        self.machine_availability[machine_name].sort()

    def find_next_available_slot(self, machine_name: str, duration: int, earliest_start: datetime) -> datetime:
        """
        Findet den nächstmöglichen Zeitpunkt, an dem eine Maschine verfügbar ist.
        
        Args:
            machine_name: Name der benötigten Maschine
            duration: Benötigte Dauer in Minuten
            earliest_start: Frühestmöglicher Startzeitpunkt
        
        Returns:
            Datetime des nächsten verfügbaren Zeitslots
        """
        current_time = earliest_start
        while not self.is_machine_available(machine_name, current_time, duration):
            current_time += timedelta(minutes=30)  # Prüfe in 30-Minuten-Schritten
        return current_time

class ProductionScheduler:
    """
    Hauptklasse für die Produktionsplanung.
    Koordiniert die Planung aller Jobs, Operationen und Ressourcen.
    """
    def __init__(self, jobs: List[Job], machines: List[Machine], 
                 operations: List[Operation], aids: List[ProductionAid],
                 materials: List[Material], buffers: List[Buffer]):
        """
        Initialisiert den Produktionsplaner mit allen notwendigen Daten.
        
        Args:
            jobs: Liste aller zu planenden Aufträge
            machines: Liste aller verfügbaren Maschinen
            operations: Liste aller möglichen Operationen
            aids: Liste aller Produktionshilfsmittel
            materials: Liste aller Materialien
            buffers: Liste aller Puffer
        """
        self.jobs = jobs
        self.machines = machines
        self.operations = operations
        self.aids = aids
        self.materials = materials
        self.buffers = buffers
        self.machine_scheduler = MachineScheduler()

    def _find_machine_for_operation(self, operation_name: str) -> Optional[Machine]:
        """
        Findet eine geeignete Maschine für eine bestimmte Operation.
        Prüft die Fertigungsfrequenzen jeder Maschine.
        """
        for machine in self.machines:
            if any(freq['Operation'] == operation_name for freq in machine.production_frequencies):
                return machine
        return None

    def _get_operation_sequence(self, operation_name: str) -> List[str]:
        """
        Ermittelt die vollständige Sequenz von Operationen, die für einen Job benötigt werden.
        Berücksichtigt die Vorgänger-Nachfolger-Beziehungen zwischen Operationen.
        
        Returns:
            Liste von Operationsnamen in der richtigen Reihenfolge
        """
        sequence = []
        current_op = operation_name
        
        while current_op:
            sequence.append(current_op)
            # Suche die aktuelle Operation in der Operationsliste
            op_data = next((op for op in self.operations if op.name == current_op), None)
            if op_data and op_data.predecessors:
                # Wenn die Operation Vorgänger hat, füge den ersten Vorgänger hinzu
                current_op = op_data.predecessors[0]
            else:
                break
                
        return list(reversed(sequence))  # Kehre die Reihenfolge um, da wir rückwärts gesucht haben

    def _map_job_to_operations(self, job_name: str) -> str:
        """
        Ordnet jedem Job seine Startoperation zu.
        Dies ist notwendig, da Jobs und Operationen unterschiedliche Namen haben können.
        """
        job_operation_map = {
            "Rahmenproduktion": "Schneiden",  # Startet mit Schneiden, dann Schweißen
            "Lackierung": "Lackieren",
            "Montage": "Montieren",
            "Verpackung": "Verpacken"
        }
        return job_operation_map.get(job_name)

    def create_schedule(self, start_date: datetime) -> List[SchedulingResult]:
        """
        Hauptmethode zur Erstellung des Produktionsplans.
        
        Args:
            start_date: Startdatum für die Planung
        
        Returns:
            Liste von SchedulingResult-Objekten, die den kompletten Produktionsplan darstellen
        """
        schedule = []
        # Sortiere Jobs nach Priorität (H > M > L) und Deadline
        sorted_jobs = sorted(self.jobs, 
                           key=lambda x: (ord('H') - ord(x.priority), x.deadline))

        
        for job in sorted_jobs:
            # Finde die Startoperation für den Job
            start_operation = self._map_job_to_operations(job.name)
            if not start_operation:
                continue

            # Ermittle die komplette Operationssequenz
            operation_sequence = self._get_operation_sequence(start_operation)
            current_time = max(start_date, job.earliest_start)
            
            # Plane jede Operation in der Sequenz
            for op_name in operation_sequence:
                operation = next((op for op in self.operations if op.name == op_name), None)
                if not operation:
                    continue

                # Finde eine geeignete Maschine
                machine = self._find_machine_for_operation(op_name)
                if not machine:
                    continue

                # Finde den nächsten verfügbaren Zeitslot
                start_time = self.machine_scheduler.find_next_available_slot(
                    machine.name, operation.required_time, current_time
                )
                
                # Reserviere die Maschine
                self.machine_scheduler.reserve_machine(
                    machine.name, start_time, operation.required_time
                )

                # Erstelle das Scheduling-Ergebnis
                end_time = start_time + timedelta(minutes=operation.required_time)
                schedule.append(SchedulingResult(
                    job_name=job.name,
                    operation_name=op_name,
                    machine_name=machine.name,
                    start_time=start_time,
                    end_time=end_time,
                    resources_used={}  # Platzhalter für zukünftige Ressourcenverwaltung
                ))

                current_time = end_time

        # Sortiere den finalen Zeitplan nach Startzeit
        return sorted(schedule, key=lambda x: x.start_time)
