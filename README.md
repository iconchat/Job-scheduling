# Übersicht der Planungskomponenten

## **1. SchedulingResult**
Speichert das Ergebnis einer einzelnen geplanten Operation.  
Enthält alle wichtigen Informationen:

- **Job**: Name des Jobs.
- **Operation**: Name der Operation.
- **Maschine**: Verwendete Maschine.
- **Zeiten**: Start- und Endzeit der Operation.
- **Kosten**: Gesamtkosten der Operation.

---

## **2. MachineScheduler**
Verwaltet die Belegung und Verfügbarkeit der Maschinen.

### **Wichtige Funktionen:**
- **Verfügbarkeit prüfen:** Stellt sicher, dass eine Maschine zu einem bestimmten Zeitpunkt verfügbar ist.
- **Zeitslots reservieren:** Blockiert einen Zeitraum für eine geplante Operation.
- **Nächsten freien Zeitslot finden:** Sucht den frühestmöglichen Zeitpunkt für eine Operation auf einer Maschine.

## **3. ProductionScheduler**
Die Hauptklasse für die Produktionsplanung.  
Koordiniert die Planung aller Jobs und Operationen.

### **Wichtige Methoden:**
1. **`_calculate_operation_cost`**  
   Berechnet die Gesamtkosten einer Operation, basierend auf Maschinen- und Operationskosten.

2. **`_find_machine_for_operation`**  
   Findet die passende Maschine für eine gegebene Operation.

3. **`_get_operation_sequence`**  
   Ermittelt die korrekte Reihenfolge der auszuführenden Operationen.

4. **`_map_job_to_operations`**  
   Ordnet Jobs ihren jeweiligen Startoperationen zu.

5. **`create_schedule`**  
   Erstellt den Gesamtzeitplan für alle Jobs und Operationen.

## **4. Planungsalgorithmus**
### **Schritte im Algorithmus (in `create_schedule`):**
1. **Sortieren der Jobs**  
   - Jobs werden basierend auf **Priorität** (H > M > L) und **Deadline** sortiert.

2. **Planung für jeden Job:**  
   - **Startoperation finden:** Ermittle die Startoperation des Jobs.
   - **Operationssequenz ermitteln:** Finde die Reihenfolge der auszuführenden Operationen.

3. **Planung jeder Operation:**  
   - **Passende Maschine finden:** Ermittle eine Maschine, die die Operation ausführen kann.
   - **Freien Zeitslot suchen:** Finde den frühestmöglichen Zeitpunkt, an dem die Maschine verfügbar ist.
   - **Maschine reservieren:** Blockiere den Zeitraum für die Operation.
   - **Kosten berechnen:** Erstelle eine Kostenberechnung für die geplante Operation.
   - **Ergebnis speichern:** Speichere das Ergebnis als `SchedulingResult`.

4. **Finaler Zeitplan:**  
   - Sortiere den Plan basierend auf den Startzeiten aller Operationen.

## **5. Berücksichtigte Faktoren**
Der Algorithmus berücksichtigt die folgenden Parameter:

- **Prioritäten der Jobs:** Höchste Priorität (H) wird zuerst behandelt, dann mittlere (M) und schließlich niedrige (L).
- **Früheste Starttermine:** Jobs können nicht vor einem bestimmten Zeitpunkt beginnen.
- **Lieferfristen:** Deadline jedes Jobs wird berücksichtigt.
- **Maschinenverfügbarkeit:** Maschinen müssen verfügbar und geeignet sein.
- **Operationsreihenfolgen:** Die logische Reihenfolge der Operationen wird eingehalten.
- **Kosten:** Operations- und Maschinenkosten werden minimiert.


