import os
import re
import json
import time
from datetime import datetime

from langgraph.graph import StateGraph, START, END, MessagesState

from typing import Annotated, Literal
from typing_extensions import TypedDict

import tiktoken

class Functions:

    def __init__(self):
        pass

    @staticmethod
    def count_tokens(text: str, model_name: str = "gpt-4o") -> int:
        encoding = tiktoken.encoding_for_model(model_name)
        return len(encoding.encode(text))

    @staticmethod
    def calculate_cost(tokens: int, model_name: str, is_input: bool) -> float:
        cost_per_token = {
            "gpt-4o": {"input": 0.000005, "output": 0.000015},
            "gpt-4o-mini": {"input": 0.00000015, "output": 0.0000006},
        }
        
        if model_name in cost_per_token:
            if is_input:
                cost = tokens * cost_per_token[model_name]["input"]
            else:
                cost = tokens * cost_per_token[model_name]["output"]
        else:
            raise ValueError(f"Model {model_name} not supported.")
        
        return round(float(cost), 6)

    @staticmethod    
    def should_continue_planificador(state: MessagesState) -> Literal["agente_alta_cliente", "agente_asistente_reclamaciones", "agente_conector_gestor_cliente", "agente_contratador", "agente_recuperador_datos", "agente_evaluador_viabilidad", "agente_gestor", "agente_generador_propuesta", "agente_gestor", END]:
        messages = state['messages']
        last_message = messages[-1]

        if last_message.additional_kwargs['agent'] == "agente_planificador":
            matches = re.findall(r'```json\s*(\{.*?\})\s*```', last_message.content, re.DOTALL)
            parsed_json = json.loads(matches[0])
            if parsed_json["next_agent"] == 'END':
                return END
            else:
                return parsed_json["next_agent"]

    @staticmethod
    def should_continue_gestor(state: MessagesState) -> Literal["agente_planificador", "cliente"]:
        messages = state['messages']
        last_message = messages[-2]

        if last_message.additional_kwargs['agent'] == "cliente":
            return 'agente_planificador'
        else:
            return 'cliente'
