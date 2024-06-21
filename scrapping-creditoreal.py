import requests
import json
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# URL base do site de onde os dados serão extraídos
base_url = "https://www.creditoreal.com.br/alugueis/florianopolis-sc?filters=%7B%22valueType%22%3Atrue%2C%22cityState%22%3A%22Florian%C3%B3polis_SC%22%7D&cityState=florianopolis-sc"

def fetch_page(url):
    """Busca o conteúdo da página e retorna um objeto BeautifulSoup"""
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.content, 'html.parser')
    else:
        print(f"Falha ao acessar a página {url}")
        return None

def parse_imovel(imovel):
    """Extrai os detalhes do imóvel do objeto BeautifulSoup fornecido"""
    section_imovel = imovel.find("section", {"class": "sc-b308a2c-0 faJViK"})

    tipoImovel_aux = section_imovel.find("span", {"class": "imovel-type"})
    rua_aux = section_imovel.find("span", {"type": "text.small", "weight": "bold"})
    endereco_aux = section_imovel.find("span", {"class": "sc-e9fa241f-1 hqggtn"})
    url_aux = 'https://www.creditoreal.com.br' + imovel['href']

    dados_imovel = section_imovel.find_all("p", {"class": "sc-e9fa241f-1"})

    area_aux = ''
    quarto_aux = ''
    vaga_aux = ''
    valor_aux = ''
    banheiro_aux = ''

    for p in dados_imovel:
        text = p.text
        if 'm²' in text:
            area_aux = text
        elif 'quarto' in text:
            quarto_aux = text
        elif 'vaga' in text:
            vaga_aux = text
        elif 'R$' in text:
            valor_aux = text.replace('\u00a0', ' ')
        elif 'banheiro' in text:
            banheiro_aux = text

    tipoImovel = tipoImovel_aux.text.strip() if tipoImovel_aux else "Sem tipo informado"
    rua = rua_aux.text.strip() if rua_aux else "Sem rua informada"
    endereco = endereco_aux.text.strip() if endereco_aux else "Sem endereço"
    url = url_aux if url_aux else "Sem url"

    area = area_aux if area_aux else "Sem área informada"
    quarto = quarto_aux if quarto_aux else "Sem quartos informados"
    vaga = vaga_aux if vaga_aux else "Sem vaga informada"
    valor = valor_aux if valor_aux else "Sem valor informado"
    banheiro = banheiro_aux if banheiro_aux else "Sem quantidade de banheiros informada"

    return {
        'TIPO': tipoImovel,
        'RUA': rua,
        'ENDERECO': endereco,
        'URL': url,
        'VALOR': valor,
        'AREA': area,
        'QUARTOS': quarto,
        'BANHEIROS': banheiro,
        'VAGAS': vaga
    }

def extract_data(page_index):
    """Extrai os dados dos imóveis de uma determinada página"""
    url = f"{base_url}&page={page_index}"
    site = fetch_page(url)
    resultados = []
    if site:
        links_imoveis = site.find_all("a", {"class": "iJQgSL"})
        if links_imoveis:
            for imovel in links_imoveis:
                resultados.append(parse_imovel(imovel))
        else:
            print(f"Não existem links dos imóveis na página {url}")
    return resultados

def main():
    resposta = []
    num_paginas = 100

    # Cria um pool de threads para fazer requisições em paralelo
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(extract_data, page) for page in range(1, num_paginas + 1)]

        # Coleta os resultados conforme as threads forem concluindo
        for future in as_completed(futures):
            resultados = future.result()
            resposta.extend(resultados)
            print(f"Total de imóveis coletados até agora: {len(resposta)}")

    # Adiciona IDs únicos e incrementais aos imóveis e coloca o ID como a primeira propriedade
    for idx, imovel in enumerate(resposta, start=1):
        imovel = {**{'ID': str(idx)}, **imovel}
        resposta[idx-1] = imovel

    # Converte os dados coletados para o formato JSON e salva em um arquivo
    json_data = json.dumps(resposta, ensure_ascii=False, indent=4)
    with open("imoveis_credito-real.json", "w", encoding='utf-8') as file:
        file.write(json_data)

    print("JSON gerado e salvo em 'imoveis_credito-real.json'")

if __name__ == "__main__":
    main()
