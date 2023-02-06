FROM python3.12.0a4-alpine3.17

#define o responsável pela aplicação
LABEL João Lucas Ferras

#Atualiza o SO
RUN apk update && apk upgrade --available -y

#Instala o python3, pip3 e o git
RUN apk add python3 python3-pip git -y

#vai para o diretório principal
WORKDIR /Verify_SSM_instaled/instance-info

#Instala o aplicativo
RUN pip3 install -r requirements.txt

# Entra na pasta do app (só é executado quando iniciamos o container)
CMD [“python3”, “app.py”]