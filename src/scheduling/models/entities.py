from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Job:
    name: str
    priority: str
    earliest_start: datetime
    deadline: datetime
    required_quantity: int

@dataclass
class Machine:
    name: str
    maintenance_time: int
    maintenance_account: int
    production_frequencies: List[dict]
    cost_per_time_unit: float

@dataclass
class Operation:
    name: str
    material_quantity: int
    min_storage_time: List[dict]
    required_time: int
    simultaneous_production: List[str]
    predecessors: List[str]
    required_aids_count: int
    cost_per_time_unit: float
    output_quantity: int

@dataclass
class ProductionAid:
    name: str
    type: str
    available_quantity: int
    cost: float

@dataclass
class Material:
    name: str
    delivery_time: int
    cost: float

@dataclass
class Buffer:
    machine_name: str
    duration: int
    cost: float
