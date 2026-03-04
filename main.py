import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import cgi # Para tratar caracteres especiais

def extrair_noticias():
    url_alvo = "https://www.camara-americana.sp.gov.br/Noticia/PaginaVereador/1?vereador=160"
    base_url = "https://www.camara-americana.sp.gov.br"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url_alvo, headers=headers)
        response.encoding = 'utf-8' # Força a codificação correta
        soup = BeautifulSoup(response.text, 'html.parser')
        itens = soup.select('li.noticia-item') or soup.select('div.noticias-lista-item')

        fg = FeedGenerator()
        fg.id(url_alvo)
        fg.title('Noticias - Renan de Angelo')
        fg.link(href=url_alvo, rel='alternate')
        # Adicionando um link de self para o validador ficar feliz
        fg.link(href='https://raw.githubusercontent.com/gustavribeiro92-boop/noticias-renan/main/feed.xml', rel='self')
        fg.description('Feed de noticias do gabinete')
        fg.language('pt-br')

        for item in itens:
            tag_link = item.find('a')
            if not tag_link: continue
            
            titulo = tag_link.find('h3').text.strip() if tag_link.find('h3') else tag_link.text.strip()
            # Limpa o link de espaços ou caracteres estranhos
            link_original = tag_link['href'].strip()
            link = base_url + link_original if link_original.startswith('/') else link_original
            
            fe = fg.add_entry()
            fe.id(link)
            fe.title(titulo)
            fe.link(href=link)
            # Adiciona um conteúdo simples para evitar o aviso de 'item sem descrição'
            fe.description(f"Noticia publicada no site da Camara de Americana: {titulo}")

        fg.rss_file('feed.xml', pretty=True) # O 'pretty' organiza o XML visualmente
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    extrair_noticias()
