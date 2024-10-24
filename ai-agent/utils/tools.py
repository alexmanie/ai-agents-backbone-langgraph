import json
from typing import Dict

class Tools:

    @staticmethod
    def evaluate_viability(client_data: Dict[str, str]) -> int:
        annual_gross_salary = int(client_data.get("annual_gross_salary"))
        debts_amount = int(client_data.get("debts_amount"))
        property_appraisal = int(client_data.get("property_appraisal"))
        loan_amount = int(client_data.get("loan_amount"))
    
        # Cálculo de la Relación Deuda-Ingreso (RDI)
        rdi = debts_amount / annual_gross_salary
    
        # Cálculo de la Relación Préstamo-Tasación (RPT)
        rpt = loan_amount / property_appraisal
    
        # Determinación del nivel de riesgo
        if rdi <= 0.3 and rpt <= 0.7:
            viability_status = "Bajo"
        elif 0.3 < rdi <= 0.5 or 0.7 < rpt <= 0.9:
            viability_status = "Moderado"
        else:
            viability_status = "Alto"
    
        loan_application = "Aprobado" if viability_status == "Bajo" else "Denegado"
    
        #Creación del archivo json
        client_data = {
            "name": client_data.get("name"),
            "last_names": client_data.get("last_names"),
            "DNI": client_data.get("DNI"),
            "viability_status": viability_status,
            "RDI": rdi,
            "RPT": rpt,
            "loan_application": loan_application
        }
    
        with open(f"data/BBDD/{client_data.get('DNI')}/viability.json", 'w', encoding='utf-8') as archivo:
            json.dump(client_data, archivo, ensure_ascii=False)
    
        return client_data