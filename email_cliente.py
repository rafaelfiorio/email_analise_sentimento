# Instalar bibliotecas necessárias
!pip install google-generativeai
!pip install pandas google-generativeai python-dotenv

# Importações
import google.generativeai as genai
from google.colab import userdata
import os
import json
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

load_dotenv()


# Carregar as variáveis de ambiente do arquivo .env
load_dotenv("/content/drive/MyDrive/Alura_Postagem_Instagram_OpenAI/chave.env")

# Acessa a chave
api_key = os.getenv('GOOGLE_API_KEY')
smtp_username = os.getenv('SMTP_USERNAME')
smtp_password = os.getenv('SMTP_PASSWORD')



# Configurar a chave da API manualmente
genai.configure(api_key=api_key)



reviews = pd.read_csv("/content/drive/MyDrive/Alura_Analise_Sentimentos/dados/reviews-entrega-MercadoAgil.csv")
reviews = reviews[["reviewer_id", "reviewer_name", "reviewer_email", "review_text"]]


modelo = "gemini-pro"


generation_config = {
  "temperature": 0,
  "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  system_instruction="""
Você é um analisador de sentimentos de uma empresa de entrega.
Você deve analisar o sentimento das avaliações de clientes apenas em relação à entrega e não à outros aspectos.
A sua análise deve responder para cada avaliação dos clientes:
  "negativo", "neutro" ou "positivo".
Dê uma nota para o sentimento de cada avaliação dos clientes, onde:
  -5 é totalmente negativo, 0 é neutro, para avaliações inconclusivas quanto à entrega, 5 é totalmente positivo.
Para as análise que resultaram valor "negativo" deve sugerir um texto de e-mail a ser enviado para o cliente.
O formato da resposta deve ser um JSON como a seguir:

```json
[
  {
  "reviewer_id": <id aqui>,
  "reviewer_name": <nome aqui>,
  "reviewer_email": <email aqui>
  "sentimento": "<sentimento aqui>"
  "nota": "<nota aqui>"
  "texto_email": "<texto email aqui>"
 }
]
```
"""
)

prompt_usuario = f"""
Analise o sentimento das avaliações do CSV a seguir:

```csv
{reviews.to_csv()}
```
"""

response = model.generate_content(prompt_usuario)
conteudo = response.text

json_resultado = json.loads(conteudo)


# Criar um DataFrame
resultados_df = pd.DataFrame(json_resultado)




# Configurações do SMTP do Mailtrap (substitua pelos seus dados)
smtp_server = "sandbox.smtp.mailtrap.io"
smtp_port = 2525


for index, row in resultados_df.iterrows():
  if row['sentimento'] == 'negativo':
    # Conteúdo do email
    sender_email = "meu_email@example.com"
    receiver_email = row['reviewer_email']  # Access email directly from row
    subject = "Email Hare Express"
    body = row['texto_email']  # Access email text directly from row

    # Criação do objeto mensagem
    message = MIMEText(body, 'plain', 'utf-8')
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject

    # Conexão com o servidor SMTP e envio do email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
      server.starttls()
      server.login(smtp_username, smtp_password)
      server.sendmail(sender_email, receiver_email, message.as_string())

