import boto3
import json

lista_de_arquivos = []

class EC2InstancesStatus:
    # Inicia a sessão.
    def __init__(self, region_name_us_east_1='us-east-1', region_name_sa_east_1='sa-east-1'):
        self.session_us_east_1 = boto3.Session(region_name=region_name_us_east_1)
        self.client_us_east_1 = self.session_us_east_1.client('ec2')
        self.client_ssm_us_east_1 = self.session_us_east_1.client('ssm')

        self.session_sa_east_1 = boto3.Session(region_name=region_name_sa_east_1)
        self.client_sa_east_1 = self.session_sa_east_1.client('ec2')
        self.client_ssm_sa_east_1 = self.session_sa_east_1.client('ssm')

    def get_status(self, client):
        instances_status = []            
        # Recebe informações sobre todas as instâncias, incluindo os Status Running, Stopped e Terminated.
        instances_info = client.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'stopped', 'terminated']}])
        
        # Iteração para retornar o status das instâncias com as devidas informações.
        for reservation in instances_info['Reservations']:
            for instance in reservation['Instances']:
                # Recebe o ID da instância.
                instance_id = instance['InstanceId']
                
                # Recebe o nome da instância, se existir.
                instance_name = [tag['Value'] for tag in instance['Tags'] if tag['Key'] == 'Name']
                
                # Verificar se o agente SSM está instalado na instância.
                ssm_response = self.client_ssm_us_east_1.describe_instance_information(Filters=[{'Key': 'InstanceIds', 'Values': [instance_id]}])

                # Condição verifica se ssm_response == True ou false.
                ssm_installed = "True" if ssm_response['InstanceInformationList'] else "False"
                
                # Se existir o nome da instância, é adicionado à lista como um dicionário,
                # se não existir, o nome é " - ".
                if instance_name:
                    instances_status.append({
                        "InstanceId": instance_id,
                        "InstanceName": instance_name[0],
                        "SSMAgentInstalled": ssm_installed,
                        "Status": instance['State']['Name']
                    })
        return instances_status

    def exec_ec2(self):
        try:
            ec2_us_east_1 = self.get_status(self.client_us_east_1) 
            ec2_sa_east_1 = self.get_status(self.client_sa_east_1) 

            if ec2_us_east_1:
                with open('EC2 - NV.json', 'w') as f:
                    json.dump(ec2_us_east_1, f, indent=4)
                lista_de_arquivos.append(
                    'EC2 - NV.json'
                )

            if ec2_sa_east_1:
                with open('EC2 - SP.json', 'w') as f:
                    json.dump(ec2_sa_east_1, f, indent=4)
                lista_de_arquivos.append(
                    'EC2 - SP.json'
                )

            return ec2_sa_east_1, ec2_us_east_1

        except Exception as e:
            print(f"Erro ao criar a sessão Boto3: {str(e)}")
            return None, None


class RDSInfo:
    def __init__(self, region_name_us_east_1='us-east-1', region_name_sa_east_1='sa-east-1'):
        self.session_us_east_1 = boto3.Session(region_name=region_name_us_east_1)
        self.client_us_east_1 = self.session_us_east_1.client('rds')

        self.session_sa_east_1 = boto3.Session(region_name=region_name_sa_east_1)
        self.client_sa_east_1 = self.session_sa_east_1.client('rds')

    def rds_describe(self, client):
        response = client.describe_db_instances()
        rds_info = []
        for instance in response['DBInstances']:
            rds_info.append({
                'DBInstanceIdentifier': instance['DBInstanceIdentifier'],
                'DBInstanceArn': instance['DBInstanceArn'],
                'Engine': instance['Engine'],
                'AvailabilityZone': instance['AvailabilityZone'],
                'DBInstanceClass': instance['DBInstanceClass']
            })
        return rds_info

    def exec_rds(self):
        rds_us_east_1 = self.rds_describe(self.client_us_east_1)

        rds_sa_east_1 = self.rds_describe(self.client_sa_east_1)

        if rds_us_east_1:
            with open('RDS - NV.json', 'w') as f:
                json.dump(rds_us_east_1, f, indent=4)
            lista_de_arquivos.append(
                    'RDS - NV.json'
                )
        
        if rds_sa_east_1:
            with open('RDS - SP.json', 'w') as f:
                json.dump(rds_sa_east_1, f, indent=4)
            lista_de_arquivos.append(
                    'RDS - SP.json'
                )
        
        return rds_sa_east_1, rds_us_east_1


class DynamoTableInfo:
    def __init__(self, regions):
        self.regions = regions
        self.dynamodb_clients = {}
        for region in regions:
            dynamodb_client = boto3.client('dynamodb', region_name=region)
            self.dynamodb_clients[region] = dynamodb_client

    def get_table_info(self):
        results = {}
        for region, dynamodb_client in self.dynamodb_clients.items():
            table_names = dynamodb_client.list_tables()['TableNames']
            if not table_names:
                continue

            region_results = []
            for table_name in table_names:
                table = dynamodb_client.describe_table(TableName=table_name)['Table']
                read_capacity_mode = table['ProvisionedThroughput']['ReadCapacityUnits']
                write_capacity_mode = table['ProvisionedThroughput']['WriteCapacityUnits']
                try:
                    billing_mode = table['BillingModeSummary']['BillingMode']
                except KeyError:
                    billing_mode = 'UNKNOWN'
                read_capacity_mode = 'ondemand' if billing_mode == 'PAY_PER_REQUEST' else read_capacity_mode
                write_capacity_mode = 'ondemand' if billing_mode == 'PAY_PER_REQUEST' else write_capacity_mode
                total_size = table['TableSizeBytes']

                region_results.append({
                    'TableName': table_name,
                    'Status': table['TableStatus'],
                    'ReadCapacityMode': read_capacity_mode,
                    'WriteCapacityMode': write_capacity_mode,
                    'TotalSize': total_size,
                    'TableClass': ''
                })

            results[region] = region_results

        return results


    def save_results_to_file(self, results):
        for region, region_results in results.items():
            if not region_results:
                continue

            filename = f"dynamo_{region}.json"
            with open(filename, 'w') as f:
                json.dump(region_results, f, indent=4)
            lista_de_arquivos.append(
                    filename
                )
