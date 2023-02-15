import pandas as pd
from classe import *

ec2 = EC2InstancesStatus()
ec2.exec_ec2()

rds = RDSInfo()
rds.exec_rds()

regions = ['sa-east-1', 'us-east-1']
dynamo_table_info = DynamoTableInfo(regions)
results = dynamo_table_info.get_table_info()
dynamo_table_info.save_results_to_file(results)

#lista com os nomes dos arquivos JSON
json_files = lista_de_arquivos

# dicionário que armazenará cada arquivo JSON convertido em DataFrame
data_frames = {}

# converter cada arquivo JSON em um DataFrame e armazenar no dicionário
for file in json_files:
    with open(file, 'r') as f:
        data_frames[file] = pd.read_json(f)

# criar um objeto ExcelWriter para salvar a planilha
writer = pd.ExcelWriter('resultados.xlsx', engine='xlsxwriter')

# salvar cada DataFrame como uma folha da planilha
for name, data in data_frames.items():
    data.to_excel(writer, sheet_name=name.split('.')[0], index=False)

# fechar o objeto ExcelWriter
writer.save()