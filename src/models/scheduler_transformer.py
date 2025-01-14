import torch
import torch.nn as nn
import numpy as np

class SchedulingTransformer(nn.Module):
    def __init__(self, d_model=256, nhead=8, num_encoder_layers=6, num_decoder_layers=6):
        super(SchedulingTransformer, self).__init__()
        
        self.d_model = d_model
        
        # Embedding layers für verschiedene Eingabefelder
        self.job_embedding = nn.Linear(5, d_model)  # für Job-Features
        self.machine_embedding = nn.Linear(5, d_model)  # für Maschinen-Features
        self.operation_embedding = nn.Linear(9, d_model)  # für Operations-Features
        
        # Positional Encoding
        self.pos_encoder = PositionalEncoding(d_model)
        
        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, batch_first=True)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_encoder_layers)
        
        # Output layer
        self.output_layer = nn.Linear(d_model, 1)  # Ausgabe der Scheduling-Priorität
    
    def prepare_data(self, raw_data):
        """
        Bereitet die rohen JSON-Daten für den Transformer vor
        """
        # Jobs verarbeiten
        jobs = []
        for job in raw_data['job']:
            job_features = [
                int(job['id'][1:]),  # Job ID als Nummer
                1 if job['Priorität'] == 'H' else (0.5 if job['Priorität'] == 'M' else 0),  # Priorität
                float(job['benötigteEndproduktmenge']),
                # Konvertiere Datum zu float (Tage seit einem Referenzdatum)
                self._date_to_float(job['Lieferfrist']),
                self._date_to_float(job['frühesterStarttermin'])
            ]
            jobs.append(job_features)
        
        # Maschinen verarbeiten
        machines = []
        for machine in raw_data['maschine']:
            machine_features = [
                int(machine['id'][1:]),
                float(machine['Wartungszeit']),
                float(machine['Wartungszeitkonto']),
                float(machine['KostenProZeiteinheit']),
                len(machine['fertigungsfrequenz'])
            ]
            machines.append(machine_features)

        # Operations verarbeiten
        operations = []
        for op in raw_data['operation']:
            op_features = [
                int(op['id'][1:]),
                float(op['Materialmenge']),
                float(op['benötigteZeit']),
                len(op['gleichzeitigeProduktion']),
                len(op['Predecessor']),
                float(op['nötigeProduktionshilfenanzahl']),
                float(op['KostenProZeiteinheit']),
                float(op['OutputMenge']),
                len(op['Mindestlagerzeit'])
            ]
            operations.append(op_features)
        
        # Konvertiere zu Torch Tensoren
        jobs_tensor = torch.FloatTensor(jobs)
        machines_tensor = torch.FloatTensor(machines)
        operations_tensor = torch.FloatTensor(operations)
        
        return jobs_tensor, machines_tensor, operations_tensor
    
    def forward(self, jobs_tensor, machines_tensor, operations_tensor):
        # Embeddings
        jobs_embedded = self.job_embedding(jobs_tensor)
        machines_embedded = self.machine_embedding(machines_tensor)
        operations_embedded = self.operation_embedding(operations_tensor)
        
        # Füge Batch-Dimension hinzu und kombiniere alle Embeddings
        jobs_embedded = jobs_embedded.unsqueeze(0)
        machines_embedded = machines_embedded.unsqueeze(0)
        operations_embedded = operations_embedded.unsqueeze(0)
        
        # Kombiniere alle Embeddings entlang der Sequenz-Dimension
        combined = torch.cat([jobs_embedded, machines_embedded, operations_embedded], dim=1)
        
        # Positional Encoding
        combined = self.pos_encoder(combined)
        
        # Transformer Encoder
        output = self.transformer_encoder(combined)
        
        # Output Layer
        scheduling_priorities = self.output_layer(output)
        
        return scheduling_priorities.squeeze(0)  # Entferne Batch-Dimension
    
    def _date_to_float(self, date_str):
        """Konvertiert ein Datum in Tage seit 2025-01-01"""
        from datetime import datetime
        date = datetime.strptime(date_str, '%Y-%m-%d')
        reference = datetime(2025, 1, 1)
        return (date - reference).days

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super(PositionalEncoding, self).__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)

    def forward(self, x):
        return x + self.pe[:, :x.size(1)]
