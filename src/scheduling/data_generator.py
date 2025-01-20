import json
import random
from datetime import datetime, timedelta
import copy
import os
from typing import Dict, List, Tuple

class BicycleProductionGenerator:
    def __init__(self, start_date=None):
        self.start_date = start_date or datetime(2024, 1, 1)
        
        # Job templates with operations
        self.job_templates = {
            "Stadtrad": {
                "operations": ["Rahmenschweißen", "Grundierung", "Lackierung", "Montage", "Qualitätskontrolle", "Verpackung"],
                "complexity": 1.0
            },
            "E-Bike": {
                "operations": ["Rahmenschweißen", "Elektronikeinbau", "Grundierung", "Lackierung", "Montage", "Qualitätskontrolle", "Verpackung"],
                "complexity": 1.4
            },
            "Mountainbike": {
                "operations": ["Rahmenschweißen", "Spezialschweißen", "Grundierung", "Speziallackierung", "Montage", "Qualitätskontrolle", "Verpackung"],
                "complexity": 1.2
            }
        }
        
        # Operation requirements based on Excel schema
        self.operation_requirements = {
            "Rahmenschweißen": {
                "Name": "Rahmenschweißen",
                "Wartungskosten": random.randint(50, 100),
                "benötigteZeit": 45,
                "Vorgänger": None,
                "AnzahlMöglicheVorgängerOperationen": 0,
                "NameWartebedingung": None,
                "BooleanLösewertknüpftMitPredecessor": False,
                "Anzahl": 1,
                "KostenProZeiteinheit": random.uniform(10, 20)
            },
            "Spezialschweißen": {
                "Name": "Spezialschweißen",
                "Wartungskosten": random.randint(50, 100),
                "benötigteZeit": 60,
                "Vorgänger": "Rahmenschweißen",
                "AnzahlMöglicheVorgängerOperationen": 1,
                "NameWartebedingung": None,
                "BooleanLösewertknüpftMitPredecessor": False,
                "Anzahl": 1,
                "KostenProZeiteinheit": random.uniform(10, 20)
            },
            "Grundierung": {
                "Name": "Grundierung",
                "Wartungskosten": random.randint(50, 100),
                "benötigteZeit": 30,
                "Vorgänger": ["Rahmenschweißen", "Spezialschweißen"],
                "AnzahlMöglicheVorgängerOperationen": 2,
                "NameWartebedingung": None,
                "BooleanLösewertknüpftMitPredecessor": False,
                "Anzahl": 1,
                "KostenProZeiteinheit": random.uniform(10, 20)
            },
            "Lackierung": {
                "Name": "Lackierung",
                "Wartungskosten": random.randint(50, 100),
                "benötigteZeit": 40,
                "Vorgänger": "Grundierung",
                "AnzahlMöglicheVorgängerOperationen": 1,
                "NameWartebedingung": None,
                "BooleanLösewertknüpftMitPredecessor": False,
                "Anzahl": 1,
                "KostenProZeiteinheit": random.uniform(10, 20)
            },
            "Speziallackierung": {
                "Name": "Speziallackierung",
                "Wartungskosten": random.randint(50, 100),
                "benötigteZeit": 50,
                "Vorgänger": "Grundierung",
                "AnzahlMöglicheVorgängerOperationen": 1,
                "NameWartebedingung": None,
                "BooleanLösewertknüpftMitPredecessor": False,
                "Anzahl": 1,
                "KostenProZeiteinheit": random.uniform(10, 20)
            },
            "Elektronikeinbau": {
                "Name": "Elektronikeinbau",
                "Wartungskosten": random.randint(50, 100),
                "benötigteZeit": 70,
                "Vorgänger": "Rahmenschweißen",
                "AnzahlMöglicheVorgängerOperationen": 1,
                "NameWartebedingung": None,
                "BooleanLösewertknüpftMitPredecessor": False,
                "Anzahl": 1,
                "KostenProZeiteinheit": random.uniform(10, 20)
            },
            "Montage": {
                "Name": "Montage",
                "Wartungskosten": random.randint(50, 100),
                "benötigteZeit": 55,
                "Vorgänger": ["Lackierung", "Speziallackierung", "Elektronikeinbau"],
                "AnzahlMöglicheVorgängerOperationen": 3,
                "NameWartebedingung": None,
                "BooleanLösewertknüpftMitPredecessor": False,
                "Anzahl": 1,
                "KostenProZeiteinheit": random.uniform(10, 20)
            },
            "Qualitätskontrolle": {
                "Name": "Qualitätskontrolle",
                "Wartungskosten": random.randint(50, 100),
                "benötigteZeit": 25,
                "Vorgänger": "Montage",
                "AnzahlMöglicheVorgängerOperationen": 1,
                "NameWartebedingung": None,
                "BooleanLösewertknüpftMitPredecessor": False,
                "Anzahl": 1,
                "KostenProZeiteinheit": random.uniform(10, 20)
            },
            "Verpackung": {
                "Name": "Verpackung",
                "Wartungskosten": random.randint(50, 100),
                "benötigteZeit": 20,
                "Vorgänger": "Qualitätskontrolle",
                "AnzahlMöglicheVorgängerOperationen": 1,
                "NameWartebedingung": None,
                "BooleanLösewertknüpftMitPredecessor": False,
                "Anzahl": 1,
                "KostenProZeiteinheit": random.uniform(10, 20)
            }
        }

        # Machine constraints based on Excel schema
        self.machine_constraints = {
            "Schweißmaschine": {
                "Name": "Schweißmaschine",
                "Minuten": 480,  # 8 hours shift
                "Dauer": 480,
                "gleichzeitigeProduktionsbedingung": "Max 2 parallel",
                "Wert": 2,
                "Umrüstung": {
                    "Name": "Schweißen Setup",
                    "RüstZeit": random.randint(15, 30),
                    "Kosten": random.uniform(50, 100)
                }
            },
            "Spezialschweißgerät": {
                "Name": "Spezialschweißgerät",
                "Minuten": 480,  # 8 hours shift
                "Dauer": 480,
                "gleichzeitigeProduktionsbedingung": "Max 1 parallel",
                "Wert": 1,
                "Umrüstung": {
                    "Name": "Spezialschweißen Setup",
                    "RüstZeit": random.randint(15, 30),
                    "Kosten": random.uniform(50, 100)
                }
            },
            "Lackierstation": {
                "Name": "Lackierstation",
                "Minuten": 480,  # 8 hours shift
                "Dauer": 480,
                "gleichzeitigeProduktionsbedingung": "Max 3 parallel",
                "Wert": 3,
                "Umrüstung": {
                    "Name": "Lackieren Setup",
                    "RüstZeit": random.randint(15, 30),
                    "Kosten": random.uniform(50, 100)
                }
            },
            "Montagemaschine": {
                "Name": "Montagemaschine",
                "Minuten": 480,  # 8 hours shift
                "Dauer": 480,
                "gleichzeitigeProduktionsbedingung": "Max 4 parallel",
                "Wert": 4,
                "Umrüstung": {
                    "Name": "Montage Setup",
                    "RüstZeit": random.randint(15, 30),
                    "Kosten": random.uniform(50, 100)
                }
            },
            "Prüfstand": {
                "Name": "Prüfstand",
                "Minuten": 480,  # 8 hours shift
                "Dauer": 480,
                "gleichzeitigeProduktionsbedingung": "Max 2 parallel",
                "Wert": 2,
                "Umrüstung": {
                    "Name": "Prüfen Setup",
                    "RüstZeit": random.randint(15, 30),
                    "Kosten": random.uniform(50, 100)
                }
            },
            "Verpackungsmaschine": {
                "Name": "Verpackungsmaschine",
                "Minuten": 480,  # 8 hours shift
                "Dauer": 480,
                "gleichzeitigeProduktionsbedingung": "Max 2 parallel",
                "Wert": 2,
                "Umrüstung": {
                    "Name": "Verpacken Setup",
                    "RüstZeit": random.randint(15, 30),
                    "Kosten": random.uniform(50, 100)
                }
            }
        }

    def generate_input_data(self, num_jobs: int, date: datetime) -> Dict:
        """Generate input data following Excel schema."""
        jobs = []
        
        for i in range(num_jobs):
            job_type = random.choice(list(self.job_templates.keys()))
            
            job = {
                "Name": f"Job_{i+1}",
                "Lieferzeit": date.strftime("%Y-%m-%d"),
                "Datum": date.strftime("%Y-%m-%d"),
                "frühesterStarttermin": date.strftime("%Y-%m-%d"),
                "benötigteEndproduktmenge": random.randint(80, 150),
                "Operationen": []
            }
            
            # Generate operations for this job
            for op_idx, op_name in enumerate(self.job_templates[job_type]["operations"]):
                operation = {
                    "Name": op_name,
                    "Wartungskosten": random.randint(50, 100),
                    "benötigteZeit": self.operation_requirements[op_name]["benötigteZeit"],
                    "Vorgänger": self.operation_requirements[op_name]["Vorgänger"],
                    "AnzahlMöglicheVorgängerOperationen": self.operation_requirements[op_name]["AnzahlMöglicheVorgängerOperationen"],
                    "NameWartebedingung": None,
                    "BooleanLösewertknüpftMitPredecessor": False,
                    "Anzahl": 1,
                    "KostenProZeiteinheit": random.uniform(10, 20)
                }
                job["Operationen"].append(operation)
            
            jobs.append(job)
        
        # Generate machine data
        machines = {}
        for name, constraints in self.machine_constraints.items():
            machines[name] = {
                "Name": name,
                "Minuten": constraints["Minuten"],
                "Dauer": constraints["Dauer"],
                "gleichzeitigeProduktionsbedingung": constraints["gleichzeitigeProduktionsbedingung"],
                "Wert": constraints["Wert"],
                "Umrüstung": constraints["Umrüstung"]
            }
        
        return {
            "jobs": jobs,
            "maschinen": machines,
            "zeitraum": {
                "start": date.strftime("%Y-%m-%d"),
                "ende": (date + timedelta(days=5)).strftime("%Y-%m-%d")
            }
        }

    def generate_output_data(self, input_data: Dict) -> Dict:
        """Generate output data following Excel schema."""
        schedule = []
        
        for job in input_data["jobs"]:
            scheduled_job = copy.deepcopy(job)
            current_time = datetime.strptime(job["frühesterStarttermin"], "%Y-%m-%d")
            
            for operation in scheduled_job["Operationen"]:
                operation.update({
                    "StartZeit": current_time.strftime("%Y-%m-%d %H:%M"),
                    "EndeZeit": (current_time + timedelta(minutes=operation["benötigteZeit"])).strftime("%Y-%m-%d %H:%M"),
                    "Kosten": operation["benötigteZeit"] * operation["KostenProZeiteinheit"]
                })
                current_time += timedelta(minutes=operation["benötigteZeit"])
            
            schedule.append(scheduled_job)
        
        return {
            "schedule": schedule,
            "maschinenauslastung": {
                name: random.uniform(0.6, 0.9)
                for name in input_data["maschinen"]
            }
        }

    def generate_dataset(self, num_days=100) -> Tuple[List[Dict], List[Dict]]:
        """Generate both input and output datasets."""
        input_datasets = []
        output_datasets = []
        current_date = self.start_date
        
        for _ in range(num_days):
            num_jobs = random.randint(8, 12)
            input_data = self.generate_input_data(num_jobs, current_date)
            output_data = self.generate_output_data(input_data)
            
            input_datasets.append(input_data)
            output_datasets.append(output_data)
            
            current_date += timedelta(days=1)
        
        return input_datasets, output_datasets

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    generator = BicycleProductionGenerator()
    input_datasets, output_datasets = generator.generate_dataset(100)
    
    # Save input data
    input_file = os.path.join(script_dir, 'data', 'scheduling_input_data.json')
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(input_datasets, f, ensure_ascii=False, indent=4)
    
    # Save output data
    output_file = os.path.join(script_dir, 'data', 'scheduling_output_data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_datasets, f, ensure_ascii=False, indent=4)
    
    print(f"Generated {len(input_datasets)} days of scheduling data:")
    print(f"Input data saved to: {input_file}")
    print(f"Output data saved to: {output_file}")

if __name__ == "__main__":
    main()
