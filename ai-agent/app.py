from flask import Flask

import os
import re
import json
import time
from datetime import datetime
import html

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END, MessagesState

from state import State
from utils.memory import CosmosDBHandler
from utils.agents import Agents
from utils.functions import Functions
from flask import request

from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/chat', methods=['GET'])
def chat() -> str:
    
    # Get the contents of the request
    conversation_id = request.args.get('conversation_id', default='', type=str)
    # Sanitize conversation_id to avoid reflected XSS if it is rendered in an HTML context
    safe_conversation_id = html.escape(conversation_id, quote=True)
    request_data = request.args.get('message', default='', type=str)
    
    HOST = os.getenv('ACCOUNT_HOST')
    MASTER_KEY = os.getenv('ACCOUNT_KEY')
    DATABASE_ID = os.getenv('COSMOS_DATABASE')
    CONTAINER_ID = os.getenv('COSMOS_CONTAINER')
    PARTITION_KEY = os.getenv('COSMOS_PARTITION_KEY')
    LOCAL_AUTH = os.getenv('COSMOS_DISABLELOCALAUTH')

    items = None
    
    if LOCAL_AUTH == "True":
        ## CosmosDB with disableLocalAuth = True
        credential = DefaultAzureCredential()
        handler = CosmosDBHandler(endpoint=HOST, credential=credential, database_name=DATABASE_ID, container_name=CONTAINER_ID)
    else:
        ## CosmosDB with disableLocalAuth = False
        handler = CosmosDBHandler(endpoint=HOST, key=MASTER_KEY, database_name=DATABASE_ID, container_name=CONTAINER_ID)
    
    if conversation_id is not None and conversation_id != "":
        items = handler.read_item(conversation_id, conversation_id)
    
    graph_builder = StateGraph(State)

    # Set nodes
    graph_builder.add_node("agente_gestor", Agents.agente_gestor)
    graph_builder.add_node("agente_planificador", Agents.agente_planificador)
    graph_builder.add_node("agente_recuperador_datos", Agents.agente_recuperador_datos)
    graph_builder.add_node("agente_alta_cliente", Agents.agente_alta_cliente)
    graph_builder.add_node("agente_asistente_reclamaciones", Agents.agente_asistente_reclamaciones)
    graph_builder.add_node("agente_conector_gestor_cliente", Agents.agente_conector_gestor_cliente)
    graph_builder.add_node("agente_contratador", Agents.agente_contratador)
    graph_builder.add_node("agente_evaluador_viabilidad", Agents.agente_evaluador_viabilidad)
    graph_builder.add_node("agente_generador_propuesta", Agents.agente_generador_propuesta)
    graph_builder.add_node("cliente", Agents.cliente)

    # Set edges
    graph_builder.set_entry_point("cliente")

    graph_builder.add_conditional_edges("agente_gestor", Functions.should_continue_gestor)
    graph_builder.add_conditional_edges("agente_planificador", Functions.should_continue_planificador)

    graph_builder.add_edge("agente_recuperador_datos", "agente_planificador")
    graph_builder.add_edge("agente_alta_cliente", "agente_planificador")
    graph_builder.add_edge("agente_asistente_reclamaciones", "agente_planificador")
    graph_builder.add_edge("agente_conector_gestor_cliente", "agente_planificador")
    graph_builder.add_edge("agente_contratador", "agente_planificador")
    graph_builder.add_edge("agente_evaluador_viabilidad", "agente_planificador")
    graph_builder.add_edge("agente_generador_propuesta", "agente_planificador")
    graph_builder.add_edge("cliente", "agente_gestor")

    graph = graph_builder.compile()
    
    historial = []
    logs = []

    fecha_hora_actual = datetime.now()
    fecha_hora_formateada = fecha_hora_actual.strftime("%Y-%m-%d_%H-%M-%S")

    es_cliente, es_despues_gestor = False, False

    if items is not None:
        # todo - alimentar historial
        historial = items["historial"]
        
        # todo - create messages list with historic data
        msg_list = []
        
        # Add initial message to start the conversation
        assistant_msg = AIMessage(content='START', additional_kwargs={"agent": "START", "user_input": historial[0]["message"]})
        msg_list.append(assistant_msg)
                
        for item in historial:
            if item["Speaker"] == "cliente":
                msg = HumanMessage(content=item["message"], additional_kwargs={"agent": "cliente", "execution_time": 0, "tokens_in":0, "cost_in":0, "tokens_out":0, "cost_out":0, "tokens_total":0, "cost_total": 0})
                msg_list.append(msg)
            elif item["Speaker"] == "agente_gestor" or item["Speaker"] == "agente_planificador":
                msg = AIMessage(content=item["message"], additional_kwargs={"agent": item["Speaker"], "execution_time": 0, "tokens_in":0, "cost_in":0, "tokens_out":0, "cost_out":0, "tokens_total":0, "cost_total": 0})
                msg_list.append(msg)
        
        # Add final message to end the conversation
        user_msg = HumanMessage(content=request_data, additional_kwargs={"agent": "cliente", "user_input": request_data, "execution_time": 0, "tokens_in":0, "cost_in":0, "tokens_out":0, "cost_out":0, "tokens_total":0, "cost_total": 0})
        msg_list.append(user_msg)
        
        dict_messages = {"messages": msg_list}
        
    else:
        # start the conversation
        assistant_msg = AIMessage(content='START', additional_kwargs={"agent": "START", "user_input": request_data})
        dict_messages = {"messages": [assistant_msg]}

    global response_msg
    response_msg = ""
    
    output = ""

    for event in graph.stream(dict_messages, RunnableConfig(recursion_limit=100)):
        
        event_items = event.items()
        event_keys = event.keys()
        values = event.values()
        
        for value in event.values():
                
            value_messages = value["messages"]
                
            agente = [key for key in event.keys()][0]
            
            # Esta lógica es para no printear los mensajes del gestor cuando habla el cliente y actúa únicamente como proxy para el planificador
            if agente == 'cliente':
                es_cliente = True
                
            if es_cliente == True:
                if agente == 'agente_gestor':
                    es_despues_gestor = True

            if (es_cliente == True and es_despues_gestor == True) == False:
                historial.append({"Speaker":agente, "message":value["messages"][-1].content})  
                
                # write new logs with tokens in, tokens out, cost in, cost out, tokens total , cost total
                # logs.append({"Speaker":agente, "message":value["messages"][-1].content, "execution_time": value["messages"][-1].additional_kwargs['execution_time'], "tokens_in": value["messages"][-1].additional_kwargs['tokens_in'], "cost_in": value["messages"][-1].additional_kwargs['cost_in'], "tokens_out": value["messages"][-1].additional_kwargs['tokens_out'], "cost_out": value["messages"][-1].additional_kwargs['cost_out'], "tokens_total": value["messages"][-1].additional_kwargs['tokens_total'], "cost_total": value["messages"][-1].additional_kwargs['cost_total']})
                
                output += "-------------------------------------------------------\n"
                output += """{agente}: {mensaje} \n""".format(agente=agente, mensaje=value["messages"][-1].content)
                output += "-------------------------------------------------------\n"
                    
                print('-------------------------------------------------------')
                print(f"{agente}:", value["messages"][-1].content)
                print('-------------------------------------------------------')
                
                # break and return the response
                if agente == 'agente_gestor':
                    response_msg = value["messages"][-1].content
                    break
                
            else:
                es_cliente , es_despues_gestor = False, False
        
        if response_msg != "":
            break

    # try:

    #     global json_datos_cliente

    #     # Crear la carpeta si no existe
    #     if not os.path.exists(f"data/BBDD/{json_datos_cliente.get('DNI')}/chat_history"):
    #         os.makedirs(f"data/BBDD/{json_datos_cliente.get('DNI')}/chat_history")

    #     with open(f"data/BBDD/{json_datos_cliente.get('DNI')}/chat_history/{fecha_hora_formateada}.json", 'w', encoding='utf-8') as archivo:
    #         json.dump(historial, archivo, ensure_ascii=False, indent=4)

    #     # Modifica el JSON de data con los datos nuevos.
    #     with open(f"data/BBDD/data.json", 'r', encoding='utf-8') as archivo:
    #         BBDD = json.load(archivo)

    #     global json_viability
    #     json_viability = json_viability

    #     actual_BBDD_data_client = [elem for elem in BBDD if elem['DNI']==json_viability['DNI']]

    #     actual_BBDD_data_client[0]['RPT'] = json_viability['RPT']
    #     actual_BBDD_data_client[0]['RDI'] = json_viability['RDI']
    #     actual_BBDD_data_client[0]['loan_application'] = json_viability['loan_application']
    #     actual_BBDD_data_client[0]['viability_status'] = json_viability['viability_status']

    #     with open(f"data/BBDD/data.json", 'w', encoding='utf-8') as archivo:
    #         json.dump(BBDD, archivo, indent=4)
            
    #     # Creamos archivo con logs (agentes, tiempos, tokens ...)
    #     with open(f"data/BBDD/{json_datos_cliente.get('DNI')}/chat_history/{fecha_hora_formateada}_logs.json", 'w', encoding='utf-8') as archivo:
    #         json.dump(logs, archivo, ensure_ascii=False, indent=4)

    # except:
    #     print("**ERROR GUARDANDO HISTÓRICO DE MENSAJES. LA CONVERSACIÓN NO PUDO SER GUARDADA**")
    
    
    if conversation_id is not None and conversation_id != "":
        # update memory item
        memory_item = {
            'id' : conversation_id,
            'partitionKey' : conversation_id,
            'historial' : historial
        }
        
        handler.update_item(conversation_id, conversation_id, memory_item)
    else:
        conversation_id = str(int(time.time()))
        memory_item = {
            'id' : conversation_id,
            'partitionKey' : conversation_id,
            'historial' : historial
        }
    
        handler.insert_item(memory_item)
    
    
    return { "conversation_id": safe_conversation_id, "response": response_msg, "output": output }


if __name__ == '__main__':
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode)