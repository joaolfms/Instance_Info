import json
import pandas as pd
from classe import EC2InstancesStatus
import os

# Função recebe como parâmetro os dados que serão convertidos
# a .json e depois .xlsx oriundos da classe EC2InstancesStatus.

def file_json(data, file_name):

    # Escreve a antrada em formato .json usando o modulo json.

    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)

    # Recebe o arquivo .json criado no step anterior e converte
    # em uma plhanilha de extenção .xlsx usando o modulo pd da 
    # biblioteca pandas.

    xlsx_file_name = file_name.split(".")[0] + ".xlsx"
    df = pd.read_json(file_name)
    df.to_excel(xlsx_file_name, index=False)

# Função criada para iniciar o mapeamento.

def start():

    # Recebe as informações nessessárias para que o mapeamento funcione corretamente.
     
    os.environ['AWS_PROFILE'] = input("Profile: ").strip()
    os.environ['AWS_DEFAULT_REGION'] = input("Region: ")
    name_file = input("Nome do arquivo que será sem a extenção: ")

    # Cria o objeto da classe e instância o objeto.

    ec2_status = EC2InstancesStatus()
    instances_status = ec2_status.get_status()

    # Inicia o mapeamento.

    file_json(instances_status, file_name=name_file.split(".")[0] + ".json")