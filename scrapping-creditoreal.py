import requests
import json
from bs4 import BeautifulSoup
import time


base_url = "https://www.creditoreal.com.br/alugueis/florianopolis-sc?filters=%7B%22valueType%22%3Atrue%2C%22cityState%22%3A%22Florian%C3%B3polis_SC%22%7D&cityState=florianopolis-sc"

def extract_data(page_index, id_imovel):
    # Monta a URL da página específica
    url = base_url + '&page=' + str(page_index)
    
    # Faz a requisição GET para a página
    requisicaoDePagina = requests.get(url)
    
    # Verifica se a requisição foi bem-sucedida
    if requisicaoDePagina.status_code == 200:
        # Extrai o conteúdo HTML da página
        pagina = requisicaoDePagina.content
        
        # Parseia o conteúdo HTML com BeautifulSoup
        site = BeautifulSoup(pagina, 'html.parser')
        
        # Encontra a ul que contém os posts

        links_imoveis = site.find_all("a", {"class": "iJQgSL"})

        if links_imoveis:
            for imovel in links_imoveis:
                section_imovel = imovel.find("section", {"class": "sc-b308a2c-0 faJViK"})

                tipoImovel_aux = section_imovel.find("span", {"class": "imovel-type"})
                rua_aux = section_imovel.find("span", {"type": "text.small", "weight":"bold"})
                endereco_aux = section_imovel.find("span", {"class": "sc-e9fa241f-1 hqggtn"})
                url_aux = 'https://www.creditoreal.com.br' + imovel['href']

                dados_imovel = section_imovel.find_all("p", {"class":"sc-e9fa241f-1"})

                area_aux = ''
                quarto_aux = ''
                vaga_aux = ''
                valor_aux = ''
                banheiro_aux = ''

                for p in dados_imovel:
                    if 'm²' in p.text:
                        area_aux = p.text
                    elif 'quarto' in p.text:
                        quarto_aux = p.text
                    elif 'vaga' in p.text:
                        vaga_aux = p.text
                    elif 'R$' in p.text:
                        valor_aux = p.text.replace('\u00a0', ' ')
                    elif 'banheiro' in p.text:
                        banheiro_aux = p.text

                tipoImovel = tipoImovel_aux.text.strip() if tipoImovel_aux else "Sem tipo informado"
                rua = rua_aux.text.strip() if rua_aux else "Sem rua informada"
                print(endereco_aux)
                endereco = endereco_aux.text.strip() if endereco_aux else "Sem endereço"        
                url = url_aux if url_aux else "Sem url"
                
                area = area_aux if area_aux != '' else "Sem área informada"
                quarto = quarto_aux if quarto_aux != '' else "Sem quartos informados"
                vaga = vaga_aux if vaga_aux != '' else "Sem vaga informada"
                valor = valor_aux if valor_aux != '' else "Sem valor informado"
                banheiro = banheiro_aux if banheiro_aux != '' else "Sem quantidade de banheiros informada"

                imovel = {
                            'ID': str(id_imovel),
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
                
                resposta.append(imovel)
                id_imovel += 1

                if id_imovel >= 1000:
                    break
        else:
            print("não existem links dos imóveis", url)
    else:
        print("Falha ao acessar a página", url)
    
    return id_imovel

# Variável para armazenar os dados coletados
resposta = []

# Definir o número de scrolls e tempo de espera
num_paginas = 100
pause_time = 2
imovel_nr = 1

# Realizar o scroll e extrair dados
for page in range(1, num_paginas):
    # Verificação para interromper se já temos 1000 instâncias
    if len(resposta) >= 1000:
        break

    time.sleep(pause_time)  # Esperar carregar novos itens
    imovel_nr = extract_data(page, imovel_nr)  # Extrair dados da página
    print(resposta)


# Converter a lista para JSON
json_data = json.dumps(resposta, ensure_ascii=False, indent=4)

# Salvar o JSON em um arquivo
with open("imoveis_credito-real.json", "w") as file:
    file.write(json_data)

print("JSON gerado e salvo em 'imoveis_credito-real.json'")
