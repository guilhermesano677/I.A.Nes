# Bibliotecas
import os
from dotenv import load_dotenv
from google import genai
import serial 
import time


# configuração de Arduino
porta = "COM3"
arduino = serial.Serial(porta,9600,timeout=1)
time.sleep(2)
# configuração do Modelo
MODELO = "gemini-2.5-flash-lite"
from gtts import gTTS
import pygame, tempfile

def falar(texto):
        arq = tempfile.NamedTemporaryFile(delete = False, suffix = ".mp3")
        arq.close()
        gTTS(texto, lang = "pt-br").save(arq.name)
        pygame.mixer.init()
        pygame.mixer.music.load(arq.name)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.quit()
        os.remove(arq.name)


def titulo():
    print("""
██╗░░░░█████╗░░░░███╗░░██╗███████╗░██████╗
██║░░░██╔══██╗░░░████╗░██║██╔════╝██╔════╝
██║░░░███████║░░░██╔██╗██║█████╗░░╚█████╗░
██║░░░██╔══██║░░░██║╚████║██╔══╝░░░╚═══██╗
██║██╗██║░░██║██╗██║░╚███║███████╗██████╔╝
╚═╝╚═╝╚═╝░░╚═╝╚═╝╚═╝░░╚══╝╚══════╝╚═════╝░""")
    print("\n")

def carregar_chave():
    load_dotenv()
    chave = (os.getenv("GOOGLE_APY_KEY"))
    if not chave:
        print("Faltando a chave dentro do arquivo .env")
        raise SystemExit(1)
    return chave

def montar_prompt(sistema,historico,pergunta):
    partes = [sistema]
    for turno in historico:
        if turno["papel"] == "Aluno":
            quem = "Aluno"
        else:
            quem = "I.A.Nes"
        partes.append(f"{quem}: {turno["texto"]}")
    partes.append(f"Aluno: {pergunta}")
    partes.append("I.A.Nes")
    return "\n".join(partes)

def perguntar_modelo(cliente,MODELO,prompt):
    resposta =cliente.models.generate_content(model=MODELO,contents=prompt)
    # print(f"Resposta ==> {resposta}")
    texto = getattr(resposta,"text","") or ""
    return texto

def main():
    os.system("cls")
    titulo()
    chave = carregar_chave()
    cliente = genai.Client(api_key=chave)
    # criar Historico
    historico = []
    print("I.A.Nes => Olá, eu sou a inteligencia artificial da disciplina IOT")
    while True:
        pergunta = input("Você => ")
        if not pergunta:
            continue
        # Comandos
        if pergunta.lower() == "sair":
            break
        
        if pergunta.lower() == "ligar led":
            arduino.write('1'.encode())
            while True:
                if arduino.in_waiting>0:
                    resposta = arduino.readline().decode().strip()
                    print(f"I.A.Nes => {resposta}")
                    falar(resposta)
                    break
            continue

        if pergunta.lower() == "desligar led":
            arduino.write('0'.encode())
            while True:
                if arduino.in_waiting>0:
                    resposta = arduino.readline().decode().strip()
                    print(f"I.A.Nes => {resposta}")
                    falar(resposta)
                    break
            continue
                

        sistema = "Voçê é um assistente. Responda em portugues do Brasil, claro, direto, e no máximo 2-3 frases"
        prompt = montar_prompt(sistema,historico,pergunta)

        # Chamar o Modelo
        resposta = perguntar_modelo(cliente,MODELO,prompt)

        historico.append({"papel":"aluno","texto":pergunta})
        historico.append({"papel":"I.A.Nes","texto": resposta})

        # Mostrar Resposta
        print(f"I.A.Nes => {resposta}")
        falar(resposta)

if __name__ == "__main__":
    main()

    