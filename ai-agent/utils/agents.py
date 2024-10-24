import os
import re
import json
import time
from datetime import datetime
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import MessagesState

from langchain_openai import AzureChatOpenAI

from utils.tools import Tools
from utils.functions import Functions

class Agents:

    def __init__(self) -> None:
        print("Environment variables are loaded:", load_dotenv())

    @staticmethod
    def agente_planificador(state: MessagesState):

        start_time = time.time()
        messages = state['messages']

        with open('data/prompts_definitivos/prompt_planificador.txt', 'r', encoding='utf-8') as file:
            prompt_planificador_txt = file.read()

        # Variables prompt
        chat_history = [f'''Agente: {message.additional_kwargs["agent"]} -- Mensaje: {message.content}''' for message in (messages[-20:])[1:]]
        query = messages[-1].content

        # Formatear el prompt con las variables
        prompt_planificador = prompt_planificador_txt.format(
            chat_history=chat_history,
            query=query
        )

        model =  AzureChatOpenAI(
            deployment_name=os.environ["MODEL_NAME_S"],
            openai_api_version=os.environ["API_VERSION_S"],
            azure_endpoint=os.environ["ENDPOINT_S"],
            openai_api_key=os.environ["API_KEY_S"],
            temperature=0.3,
            streaming=True
        )

        response = model.invoke(prompt_planificador)

        end_time = time.time()
        execution_time = end_time - start_time

        tokens_in = Functions.count_tokens(prompt_planificador, model_name="gpt-4o")
        cost_in = Functions.calculate_cost(tokens_in, model_name="gpt-4o", is_input=True)
        tokens_out = Functions.count_tokens(response.content, model_name="gpt-4o")
        cost_out = Functions.calculate_cost(tokens_out, model_name="gpt-4o", is_input=False)

        tokens_total = tokens_in + tokens_out
        cost_total = cost_in + cost_out

        return {"messages": [AIMessage(content=response.content, additional_kwargs={"agent": "agente_planificador", "execution_time": execution_time, "tokens_in":tokens_in, "cost_in":cost_in, "tokens_out":tokens_out, "cost_out":cost_out, "tokens_total":tokens_total, "cost_total": cost_total})]}

    @staticmethod
    def agente_gestor(state: MessagesState):
        start_time = time.time()
        messages = state['messages']
        last_message = messages[-1].content
        chat_history = [f'''Agente: {message.additional_kwargs["agent"]} -- Mensaje: {message.content}''' for message in (messages[-20:])[1:]]

        # Leer el prompt del archivo .txt
        with open('data/prompts_definitivos/prompt_gestor.txt', 'r', encoding='utf-8') as file:
            prompt_gestor_txt = file.read()
        with open('data/prompts_definitivos/extras_prompts/FAQS.txt', 'r', encoding='utf-8') as file:
            faqs_txt = file.read()
        with open('data/prompts_definitivos/extras_prompts/politicas.txt', 'r', encoding='utf-8') as file:
            politicas = file.read()

        # Si el mensaje anterior viene del cliente es ignorado (ya que el gestor se lo pasa al planificador directamente)
        if messages[-1].additional_kwargs['agent'] == "cliente":
            return {"messages": [AIMessage(content=last_message, additional_kwargs={"agent": "agente_gestor"})]}
        else:
            # Si el mensaje que le llega no es del cliente, será del planificador
            matches = re.findall(r'```json\s*(\{.*?\})\s*```', last_message, re.DOTALL)
            parsed_json = json.loads(matches[0])
            
            status =  parsed_json["status"]
            
            # Formatear el prompt con las variables
            prompt_gestor = prompt_gestor_txt.format(
                faqs_txt=faqs_txt,
                query=last_message,
                status=status,
                politicas=politicas,
                chat_history=chat_history
            )
            
            model =  AzureChatOpenAI(
                deployment_name=os.environ["MODEL_NAME_S"],
                openai_api_version=os.environ["API_VERSION_S"],
                azure_endpoint=os.environ["ENDPOINT_S"],
                openai_api_key=os.environ["API_KEY_S"],
                temperature=0.3,
                streaming=True
            )
            
            response = model.invoke(prompt_gestor)
        
            end_time = time.time()
            execution_time = end_time - start_time

            tokens_in = Functions.count_tokens(prompt_gestor, model_name="gpt-4o")
            cost_in = Functions.calculate_cost(tokens_in, model_name="gpt-4o", is_input=True)
            tokens_out = Functions.count_tokens(response.content, model_name="gpt-4o")
            cost_out = Functions.calculate_cost(tokens_out, model_name="gpt-4o", is_input=False)

            tokens_total = tokens_in + tokens_out
            cost_total = cost_in + cost_out

            return {"messages": [AIMessage(content=response.content, additional_kwargs={"agent": "agente_gestor", "execution_time": execution_time, "tokens_in":tokens_in, "cost_in":cost_in, "tokens_out":tokens_out, "cost_out":cost_out, "tokens_total":tokens_total, "cost_total": cost_total})]}
    
    # Agente Generador Propuesta
    @staticmethod
    def agente_generador_propuesta(state: MessagesState):
        start_time = time.time()
        
        # Leer el prompt del archivo .txt
        with open('data/prompts_definitivos/prompt_generador_propuesta.txt', 'r', encoding='utf-8') as file:
            prompt_generador_propuesta_txt = file.read()

        with open('data/prompts_definitivos/extras_prompts/propuesta_aceptada.txt', 'r', encoding='utf-8') as file:
            mortage_aproved_message_txt = file.read()

        with open('data/prompts_definitivos/extras_prompts/propuesta_denegada.txt', 'r', encoding='utf-8') as file:
            mortage_denied_message_txt = file.read()

        global json_viability
        global json_datos_cliente

        fecha_hora_actual = datetime.now()
        fecha_hora_formateada = fecha_hora_actual.strftime("%Y-%m-%d_%H-%M-%S")

        mortage_aproved_message = mortage_aproved_message_txt.format(
            date=fecha_hora_formateada,
            name=json_viability.get('name'),
            last_names=json_viability.get('last_names'),
            DNI=json_viability.get('DNI'),
            loan_amount=json_datos_cliente.get('loan_amount'),
            interest_rate=15,
            loan_term_in_years=15,
            monthly_payment=15,
            property_appraisal=json_datos_cliente.get('property_appraisal'),
            RPT=json_viability.get('RPT'),
            RDI=json_viability.get('RDI'),
            viability_status=json_viability.get('viability_status')
        )

        mortage_denied_message = mortage_denied_message_txt.format(
            date=fecha_hora_formateada,
            name=json_viability.get('name'),
            last_names=json_viability.get('last_names'),
            DNI=json_viability.get('DNI'),
            RPT=json_viability.get('RPT'),
            RDI=json_viability.get('RDI')
        )

        # Formatear el prompt con las variables
        prompt_generador_propuesta = prompt_generador_propuesta_txt.format(
            mortage_aproved_message=mortage_aproved_message,
            mortage_denied_message=mortage_denied_message,
            loan_application=json_viability.get('loan_application')
        )

        model =  AzureChatOpenAI(
            deployment_name=os.environ["MODEL_NAME_S"],
            openai_api_version=os.environ["API_VERSION_S"],
            azure_endpoint=os.environ["ENDPOINT_S"],
            openai_api_key=os.environ["API_KEY_S"],
            temperature=0.3,
            streaming=True
        )

        response = model.invoke(prompt_generador_propuesta)
        
        #Guarda la propuesta en un txt
        with open(f"data/BBDD/{json_viability.get('DNI')}/propuesta.txt", 'w', encoding='utf-8') as archivo:
            archivo.write(response.content)

        # Modifica el JSON de data con los datos nuevos para indicar que tiene propuesta generada.
        with open(f"data/BBDD/data.json", 'r', encoding='utf-8') as archivo:
            BBDD = json.load(archivo)

        actual_BBDD_data_client = [elem for elem in BBDD if elem['DNI']==json_viability['DNI']]

        actual_BBDD_data_client[0]['generated_proposal'] = 'Yes'

        with open(f"data/BBDD/data.json", 'w', encoding='utf-8') as archivo:
            json.dump(BBDD, archivo, indent=4)

        end_time = time.time()
        execution_time = end_time - start_time

        tokens_in = Functions.count_tokens(prompt_generador_propuesta, model_name="gpt-4o")
        cost_in = Functions.calculate_cost(tokens_in, model_name="gpt-4o", is_input=True)
        tokens_out = Functions.count_tokens(response.content, model_name="gpt-4o")
        cost_out = Functions.calculate_cost(tokens_out, model_name="gpt-4o", is_input=False)

        tokens_total = tokens_in + tokens_out
        cost_total = cost_in + cost_out
        
        return {"messages": [AIMessage(content=response.content, additional_kwargs={"agent": "agente_generador_propuesta", "execution_time": execution_time, "tokens_in":tokens_in, "cost_in":cost_in, "tokens_out":tokens_out, "cost_out":cost_out, "tokens_total":tokens_total, "cost_total": cost_total})]}

    # Agente Contratador
    @staticmethod
    def agente_contratador(state: MessagesState):
        start_time = time.time()
        # # Leer el prompt del archivo .txt
        # with open('data/prompts_definitivos/prompt_contratador.txt', 'r', encoding='utf-8') as file:
        #     prompt_contratador_txt = file.read()

        # response = model.invoke(prompt_contratador_txt)
        output = '**LA HIPOTECA HA SIDO CONTRATADA CON ÉXITO**'
        end_time = time.time()
        execution_time = end_time - start_time

        # tokens_in = count_tokens(prompt_contratador_txt, model_name="gpt-4o")
        # cost_in = calculate_cost(tokens_in, model_name="gpt-4o")
        # tokens_out = count_tokens(response.content, model_name="gpt-4o")
        # cost_out = calculate_cost(tokens_out, model_name="gpt-4o")

        tokens_in = 0
        cost_in = 0
        tokens_out = 0
        cost_out = 0

        tokens_total = tokens_in + tokens_out
        cost_total = cost_in + cost_out
        
        return {"messages": [AIMessage(content=output, additional_kwargs={"agent": "agente_contratador", "execution_time": execution_time, "tokens_in":tokens_in, "cost_in":cost_in, "tokens_out":tokens_out, "cost_out":cost_out, "tokens_total":tokens_total, "cost_total": cost_total})]}

    # Agente Evaluador Viabilidad (Tool para acceder al JSON de datos y evaluar la viabilidad)
    @staticmethod
    def agente_evaluador_viabilidad(state: MessagesState):
        start_time = time.time()
        global json_datos_cliente 
        global json_viability
        
        json_datos_cliente = json_datos_cliente
        # print('EVALUADOR: json_datos_cliente:', json_datos_cliente)
        json_viability = Tools.evaluate_viability(json_datos_cliente)
        # print('EVALUADOR: json_viability:', json_viability)

        # # Leer el prompt del archivo .txt
        # with open('data/prompts_definitivos/prompt_evaluador_viabilidad.txt', 'r', encoding='utf-8') as file:
        #     prompt_evaluador_viabilidad_txt = file.read()

        # prompt_evaluador_viabilidad = prompt_evaluador_viabilidad_txt.format(
        #     json_viability = json_viability
        # )
        
        # response = model.invoke(prompt_evaluador_viabilidad)
        output = f"**LA SOLICITUD DEL PRÉSTAMO HIPOTECARIO HA SIDO {json_viability.get('loan_application')}**"
        end_time = time.time()
        execution_time = end_time - start_time

        # tokens_in = count_tokens(prompt_planificador, model_name="gpt-4o")
        # cost_in = calculate_cost(tokens_in, model_name="gpt-4o")
        # tokens_out = count_tokens(response.content, model_name="gpt-4o")
        # cost_out = calculate_cost(tokens_out, model_name="gpt-4o")

        tokens_in = 0
        cost_in = 0
        tokens_out = 0
        cost_out = 0

        tokens_total = tokens_in + tokens_out
        cost_total = cost_in + cost_out
        
        return {"messages": [AIMessage(content=output, additional_kwargs={"agent": "agente_evaluador_viabilidad", "execution_time": execution_time, "tokens_in":tokens_in, "cost_in":cost_in, "tokens_out":tokens_out, "cost_out":cost_out, "tokens_total":tokens_total, "cost_total": cost_total})]}

    # Agente Asistente Reclamaciones (Tool para guardar la reclamación)
    @staticmethod
    def agente_asistente_reclamaciones(state: MessagesState):
        start_time = time.time()
        # # Leer el prompt del archivo .txt
        # with open('data/prompts_definitivos/prompt_asistente_reclamaciones.txt', 'r', encoding='utf-8') as file:
        #     prompt_asistente_reclamaciones_txt = file.read()

        # response = model.invoke(prompt_asistente_reclamaciones_txt)

        output = 'Para poner una reclamación al banco deberás acceder al siguiente enlace: www.reclamaciones.es Gracias por tu paciencia y lamentamos no haberle podido ayudarle. Que tenga un buen día.'
        end_time = time.time()
        execution_time = end_time - start_time

        # tokens_in = count_tokens(prompt_planificador, model_name="gpt-4o")
        # cost_in = calculate_cost(tokens_in, model_name="gpt-4o")
        # tokens_out = count_tokens(response.content, model_name="gpt-4o")
        # cost_out = calculate_cost(tokens_out, model_name="gpt-4o")

        tokens_in = 0
        cost_in = 0
        tokens_out = 0
        cost_out = 0

        tokens_total = tokens_in + tokens_out
        cost_total = cost_in + cost_out
        
        return {"messages": [AIMessage(content=output, additional_kwargs={"agent": "agente_asistente_reclamaciones", "execution_time": execution_time, "tokens_in":tokens_in, "cost_in":cost_in, "tokens_out":tokens_out, "cost_out":cost_out, "tokens_total":tokens_total, "cost_total": cost_total})]}

    # Agente Datos  Cliente
    @staticmethod
    def agente_recuperador_datos(state: MessagesState):
        start_time = time.time()
        messages = state['messages']
        # messages[-2] para que recupere el mensaje del cliente, no el del planificador
        last_message = messages[-2].content
        
        # Leer el prompt del archivo .txt
        with open('data/prompts_definitivos/prompt_recuperador_datos.txt', 'r', encoding='utf-8') as file:
            prompt_recuperador_datos_txt = file.read()
        with open(f"data/BBDD/data.json", 'r', encoding='utf-8') as archivo:
            json_data = json.load(archivo)

        # Formatear el prompt con las variables
        prompt_recuperador_datos = prompt_recuperador_datos_txt.format(
            json_data=json_data,
            last_message=last_message
        )

        model = AzureChatOpenAI(
            deployment_name=os.environ["MODEL_NAME_S"],
            openai_api_version=os.environ["API_VERSION_S"],
            azure_endpoint=os.environ["ENDPOINT_S"],
            openai_api_key=os.environ["API_KEY_S"],
            temperature=0.3,
            streaming=True
        )

        response = model.invoke(prompt_recuperador_datos)

        matches = re.findall(r'```json\s*(\{.*?\})\s*```', response.content, re.DOTALL)

        global json_datos_cliente
        json_datos_cliente = json.loads(matches[0])

        # datos_faltantes = 'Necesito los siguientes datos: '

        # # Lista de claves a excluir del chequeo
        # claves_excluidas = ["viability_status", "loan_application", "RDI", "RPT", "generated_proposal"]


        # # Chequeo de datos faltantes excluyendo las claves no deseadas
        # if any(json_datos_cliente[key] == '' or json_datos_cliente[key] == None for key in json_datos_cliente.keys() if key not in claves_excluidas):
        #     datos_faltantes = ', '.join([key for key in json_datos_cliente.keys() if (json_datos_cliente[key] == '' or json_datos_cliente[key] == None) and key not in claves_excluidas])
        #     datos_faltantes = f'Faltan los siguientes datos: {datos_faltantes}. Solicitárselos al cliente.'
        # else:
        #     datos_faltantes = f'Están todos los datos completados. Esperando que el cliente valide si los datos son correctos.'

        # output = f'Actualmente los datos de los que disponemos del usuario solicitado son: {json_datos_cliente}. {datos_faltantes}'
        output = f'Actualmente los datos de los que disponemos del usuario solicitado son: {json_datos_cliente}.'

        end_time = time.time()
        execution_time = end_time - start_time

        tokens_in = Functions.count_tokens(prompt_recuperador_datos, model_name="gpt-4o")
        cost_in = Functions.calculate_cost(tokens_in, model_name="gpt-4o", is_input=True)
        tokens_out = Functions.count_tokens(response.content, model_name="gpt-4o")
        cost_out = Functions.calculate_cost(tokens_out, model_name="gpt-4o", is_input=False)

        tokens_total = tokens_in + tokens_out
        cost_total = cost_in + cost_out
        
        return {"messages": [AIMessage(content=output, additional_kwargs={"agent": "agente_recuperador_datos", "execution_time": execution_time, "tokens_in":tokens_in, "cost_in":cost_in, "tokens_out":tokens_out, "cost_out":cost_out, "tokens_total":tokens_total, "cost_total": cost_total})]}

    # Agente Conector Gestor-Cliente (Tool Enviar enlace al cliente para que pueda comunicarse con un gestor real.)
    @staticmethod
    def agente_conector_gestor_cliente(state: MessagesState):
        start_time = time.time()
        # # Leer el prompt del archivo .txt
        # with open('data/prompts_definitivos/prompt_conector_gestor_cliente.txt', 'r', encoding='utf-8') as file:
        #     prompt_conector_gestor_cliente_txt = file.read()

        # response = model.invoke(prompt_conector_gestor_cliente_txt)

        output = '''Gracias por haber utilizado el servicio y disculpe si no se ha podido solucionar su consulta. Para contactar con un gestor deberá seguir los siguientes pasos:
            ' 1. Acceder a la Web del banco
            2. Click en la sección contacto con un gestor
            3. Chat con el gestor

            También puedes contactar con un gestor accediendo al siguiente enlace <enlace>. o enviando un correo electrónico a la siguiente dirección: gestor@mail.com'''
        
        end_time = time.time()
        execution_time = end_time - start_time

        # tokens_in = count_tokens(prompt_planificador, model_name="gpt-4o")
        # cost_in = calculate_cost(tokens_in, model_name="gpt-4o")
        # tokens_out = count_tokens(response.content, model_name="gpt-4o")
        # cost_out = calculate_cost(tokens_out, model_name="gpt-4o")

        tokens_in = 0
        cost_in = 0
        tokens_out = 0
        cost_out = 0

        tokens_total = tokens_in + tokens_out
        cost_total = cost_in + cost_out

        return {"messages": [AIMessage(content=output, additional_kwargs={"agent": "agente_conector_gestor_cliente", "execution_time": execution_time, "tokens_in":tokens_in, "cost_in":cost_in, "tokens_out":tokens_out, "cost_out":cost_out, "tokens_total":tokens_total, "cost_total": cost_total})]}

    # Agente Alta Cliente (Tool para acceder al JSON de datos y añadir un nuevo cliente)
    @staticmethod
    def agente_alta_cliente(state: MessagesState):
        start_time = time.time()
        messages = state['messages']

        # Leer el prompt del archivo .txt
        with open('data/prompts_definitivos/prompt_alta_cliente.txt', 'r', encoding='utf-8') as file:
            prompt_alta_cliente_txt = file.read()

        chat_history = [f'''Agente: {message.additional_kwargs["agent"]} -- Mensaje: {message.content}''' for message in (messages[-20:])[1:]]

        # Formatear el prompt con las variables
        prompt_alta_cliente = prompt_alta_cliente_txt.format(
            chat_history=chat_history
        )

        model = AzureChatOpenAI(
            deployment_name=os.environ["MODEL_NAME_S"],
            openai_api_version=os.environ["API_VERSION_S"],
            azure_endpoint=os.environ["ENDPOINT_S"],
            openai_api_key=os.environ["API_KEY_S"],
            temperature=0.3,
            streaming=True
        )

        response = model.invoke(prompt_alta_cliente)
        # response = self.model.invoke(prompt_alta_cliente)

        matches = re.findall(r'```json\s*(\{.*?\})\s*```', response.content, re.DOTALL)

        registro_cliente = json.loads(matches[0])
        
        with open(f"data/BBDD/data.json", 'r', encoding='utf-8') as archivo:
            json_content = json.load(archivo)

        json_content.append(registro_cliente)

        with open(f"data/BBDD/data.json", 'w', encoding='utf-8') as archivo:
            json.dump(json_content, archivo, indent=4, ensure_ascii=False)
        
        global json_datos_cliente 
        json_datos_cliente = registro_cliente


        user_folder_path = f"data/BBDD/{registro_cliente.get('DNI')}"
        # Crear la carpeta si no existe
        if not os.path.exists(user_folder_path):
            os.makedirs(user_folder_path)
        
        output = f'El cliente con datos: {registro_cliente} ha sido dado de alta correctamente.'

        end_time = time.time()
        execution_time = end_time - start_time

        tokens_in = Functions.count_tokens(prompt_alta_cliente, model_name="gpt-4o")
        cost_in = Functions.calculate_cost(tokens_in, model_name="gpt-4o", is_input=True)
        tokens_out = Functions.count_tokens(response.content, model_name="gpt-4o")
        cost_out = Functions.calculate_cost(tokens_out, model_name="gpt-4o", is_input=False)

        tokens_total = tokens_in + tokens_out
        cost_total = cost_in + cost_out
        
        return {"messages": [AIMessage(content=output, additional_kwargs={"agent": "agente_alta_cliente", "execution_time": execution_time, "tokens_in":tokens_in, "cost_in":cost_in, "tokens_out":tokens_out, "cost_out":cost_out, "tokens_total":tokens_total, "cost_total": cost_total})]}

    # Agente Hipoteca
    @staticmethod
    def cliente(state: MessagesState):

        # user_input = "quiero contratar una hipoteca"
        
        try:
            user_input = state['messages'][-1].additional_kwargs["user_input"]
        except KeyError:
            user_input = "default input"

        # user_input = input("User: ")
        # start_time = time.time()
        # end_time = time.time()
        # execution_time = end_time - start_time

        # tokens_in = count_tokens(prompt_planificador, model_name="gpt-4o")
        # cost_in = calculate_cost(tokens_in, model_name="gpt-4o")
        # tokens_out = count_tokens(response.content, model_name="gpt-4o")
        # cost_out = calculate_cost(tokens_out, model_name="gpt-4o")

        execution_time = 0
        
        tokens_in = 0
        cost_in = 0
        tokens_out = 0
        cost_out = 0

        tokens_total = tokens_in + tokens_out
        cost_total = cost_in + cost_out
        
        # TODO - si el mensaje de entrada ya es un HumanMessage, lo quitamos del listado de mensajes
        # para que no se repita en el historial
        if state['messages'][-1].__class__.__name__ == "HumanMessage":
            state['messages'] = state['messages'][:-1]
              
        return {"messages": [HumanMessage(content=user_input, additional_kwargs={"agent": "cliente", "execution_time": execution_time, "tokens_in":tokens_in, "cost_in":cost_in, "tokens_out":tokens_out, "cost_out":cost_out, "tokens_total":tokens_total, "cost_total": cost_total})]}
