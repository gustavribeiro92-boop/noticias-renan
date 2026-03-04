import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

def extrair_noticias():
    # URL oficial do Renan na Câmara e o link onde o seu RSS vai morar no GitHub
    url_alvo = "https://www.camara-americana.sp.gov.br/Noticia/PaginaVereador/1?vereador=160"
    base_url = "https://www.camara-americana.sp.gov.br"
    link_rss_final = "https://raw.githubusercontent.com/gustavribeiro92-boop/noticias-renan/main/feed.xml"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(url_alvo, headers=headers)
        response.encoding = 'utf-8' # Garante que os acentos das notícias fiquem corretos
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Seleciona os itens de notícia conforme a estrutura do site da Câmara
        itens = soup.select('li.noticia-item') or soup.select('div.noticias-lista-item')

        fg = FeedGenerator()
        fg.id(url_alvo)
        fg.title('Notícias - Renan de Angelo')
        fg.link(href=url_alvo, rel='alternate')
        
        # CORREÇÃO DO VALIDADOR: Define o link 'self' para o Atom
        fg.link(href=link_rss_final, rel='self')
        
        fg.description('Feed oficial de notícias da Câmara Municipal de Americana - Vereador Renan de Angelo')
        fg.language('pt-br')

        for item in itens:
            tag_link = item.find('a')
            if not tag_link:
                continue
            
            # Extrai título e reconstrói o link completo da notícia
            titulo = tag_link.find('h3').text.strip() if tag_link.find('h3') else tag_link.text.strip()
            href_limpo = tag_link['href'].strip()
            link_completo = base_url + href_limpo if href_limpo.startswith('/') else href_limpo
            
            # Tenta pegar a data de publicação se disponível
            tag_data = item.find('span', class_='data')
            data_desc = f"Publicado em: {tag_data.text.strip()}" if tag_data else "Notícia da Câmara Municipal"

            fe = fg.add_entry()
            fe.id(link_completo)
            fe.title(titulo)
            fe.link(href=link_completo)
            fe.description(data_desc)

        # Gera o arquivo XML formatado (pretty)
        fg.rss_file('feed.xml', pretty=True)
        print("Sucesso: feed.xml gerado e validado!")

    except Exception as e:
        print(f"Erro ao processar o feed: {e}")

if __name__ == "__main__":
    extrair_noticias()
