import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def varrer_concursos():
    # Aqui o robô acessa o site especializado (exemplo: PCI Concursos Centro-Oeste)
    url = "https://www.pciconcursos.com.br/concursos/centro-oeste/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Erro ao acessar o site: {e}")
        return {}

    alertas_novos = {}
    
    # O robô vasculha todos os links de concursos na página
    for item in soup.find_all('div', class_='caixa_concurso'):
        texto = item.get_text().upper()
        
        # Se achar algo sobre o TCDF com novidade
        if 'TRIBUNAL DE CONTAS' in texto and 'DF' in texto:
            if 'RESULTADO' in texto or 'GABARITO' in texto:
                alertas_novos['TCDF'] = "⚠️ NOVO RESULTADO/GABARITO PUBLICADO!"
            elif 'RETIFICAÇÃO' in texto or 'RETIFICADO' in texto:
                alertas_novos['TCDF'] = "⚠️ EDITAL RETIFICADO RECENTEMENTE."

        # Se achar algo sobre a PCDF
        if 'POLÍCIA CIVIL' in texto and 'CUSTÓDIA' in texto:
            if 'CEBRASPE' in texto or 'FGV' in texto or 'BANCA' in texto:
                alertas_novos['PCDF'] = "⚠️ BANCA ORGANIZADORA DEFINIDA!"

    return alertas_novos

def atualizar_painel(alertas):
    # Abre o arquivo HTML atual
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Atualiza a hora da última sincronização no topo do site
    agora = datetime.now().strftime("%d/%m/%Y às %H:%M")
    html = re.sub(
        r'id="dataAtualizacao">.*?<', 
        f'id="dataAtualizacao">Atualizado em {agora}<', 
        html
    )

    # 2. Se encontrou novidades, injeta no código JS
    if alertas:
        linhas_js = []
        for orgao, mensagem in alertas.items():
            # Cria a estrutura exata para injetar no alerta vermelho
            linhas_js.append(f"'{orgao}': {{ historico: '<span class=\"text-red-600 font-black animate-pulse\">{mensagem}</span>' }}")
        
        # Constrói o objeto dadosAutomaticos
        bloco_js = "const dadosAutomaticos = { " + ", ".join(linhas_js) + " };"
        
        # Substitui no HTML
        html = re.sub(
            r'const dadosAutomaticos = \{.*?\};', 
            bloco_js, 
            html,
            flags=re.DOTALL
        )
        print(f"Sucesso! Injetado: {alertas}")
    else:
        print("Nenhuma novidade bombástica encontrada hoje.")

    # Salva o arquivo HTML modificado
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == "__main__":
    print("Robô iniciou a varredura...")
    alertas = varrer_concursos()
    atualizar_painel(alertas)
    print("Processo finalizado.")
