import boto3

# Classe criada mapear todas as instâncias do ambiente na região definida 
# retornando as infomações de cada instância (Name, ID, SSM_Installed e Status).
class EC2InstancesStatus:
    # Inicia a sessão.
    def __init__(self):
        self.ec2 = boto3.client('ec2')
        self.ssm = boto3.client('ssm')
        
    def get_status(self):
        # Recebe informações sobre todas as instâncias, incluindo os Status Running, Stooped e Terminate.
        instances_info = self.ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'stopped', 'terminated']}])
        
        # Criar uma lista vazia para armazenar informações da instância.
        instances_status = []
        
        # Iteração para retornar o status das instâncias com as devidas informações.
        for reservation in instances_info['Reservations']:
            for instance in reservation['Instances']:
                # Recebe o ID da instância.
                instance_id = instance['InstanceId']
                
                # recebe o nome da instância, se existir.
                instance_name = [tag['Value'] for tag in instance['Tags'] if tag['Key'] == 'Name']
                
                # Verificar se o agente SSM está instalado na instância.
                ssm_response = self.ssm.describe_instance_information(Filters=[{'Key': 'InstanceIds', 'Values': [instance_id]}])

                # Condição verifica se ssm_response == True ou false.
                ssm_installed = "True" if ssm_response['InstanceInformationList'] else "False"
                
                # Se existir existir o nome da instâncias é adicionado a lista como um dicionário
                # se não existir rebe o nome como " - ".
                if instance_name:
                    instances_status.append({
                        "InstanceId": instance_id,
                        "InstanceName": instance_name[0],
                        "SSMAgentInstalled": " - " if instance['State']['Name'] in ['stopped', 'terminated'] else ssm_installed,
                        "Status": instance['State']['Name']
                    })
        
        # Retornar a lista de instâncias e suas informações.
        return instances_status

