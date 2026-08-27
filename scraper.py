import requests
from bs4 import BeautifulSoup
import re
import json

print("Iniciando a busca por novos concursos no Centro-Oeste/DF...")

# 1. Acessar o site de concursos (exemplo: PCI Concursos)
url = "https://www.pciconcursos.com.br/concursos/centroeste/"
resposta = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(resposta.text, 'html.parser')

novos_dados = {}
contador = 1

# 2. Extrair vagas do DF ou Brasília
for concurso in soup.find_all('div', class_='caixa_concurso'):
    titulo_elem = concurso.find('a')
    if titulo_elem:
        titulo = titulo_elem.text.strip()
        
        # Filtra apenas o que é do DF
        if 'DF' in titulo or 'Brasília' in titulo:
            vagas = concurso.find('div', class_='vagas')
            nivel = concurso.find('div', class_='nivel')
            link = titulo_elem['href']
            
            chave = f"AUTOMATICO_DF_{contador}"
            novos_dados[chave] = {
                "titulo": titulo,
                "status": f"Vagas: {vagas.text.strip() if vagas else 'A definir'} | Nível: {nivel.text.strip() if nivel else 'Diversos'}",
                "historico": "Identificado automaticamente pelo robô hoje.",
                "link": link
            }
            contador += 1

print(f"Encontrados {contador - 1} concursos. Atualizando o HTML...")

# 3. Ler o seu arquivo HTML (agora chamado index.html)
nome_arquivo = 'index.html'
with open(nome_arquivo, 'r', encoding='utf-8') as f:
    html = f.read()

# 4. Injetar os dados novos no lugar dos antigos
if novos_dados:
    dados_json = json.dumps(novos_dados, ensure_ascii=False, indent=4)
    novo_html = re.sub(
        r'const dadosAuditoria = \{.*?\};', 
        f'const dadosAuditoria = {dados_json};', 
        html, 
        flags=re.DOTALL
    )

    # 5. Salvar o arquivo atualizado
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write(novo_html)
    print("Painel atualizado com sucesso!")
else:
    print("Nenhum concurso novo encontrado. HTML mantido.")
