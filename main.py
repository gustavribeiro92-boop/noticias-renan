import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

def extrair_noticias():
    url_alvo = "https://www.camara-americana.sp.gov.br/Noticia/PaginaVereador/1?vereador=160"
    base_url = "https://www.camara-americana.sp.gov.br"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url_alvo, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # O seletor abaixo busca os links de notícias na listagem da Câmara
        itens_noticia = soup.select('div.noticias-lista-item') or soup.find_all('li', class_='noticia-item')

        fg = FeedGenerator()
        fg.id(url_alvo)
        fg.title('Notícias - Renan de Angelo')
        fg.link(href=url_alvo, rel='alternate')
        fg.description('Feed oficial de notícias da Câmara de Americana')
        fg.language('pt-br')

        for item in itens_noticia:
            tag_link = item.find('a')
            if not tag_link: continue
            
            titulo = tag_link.find('h3').text.strip() if tag_link.find('h3') else tag_link.text.strip()
            link_completo = base_url + tag_link['href']
            
            fe = fg.add_entry()
            fe.id(link_completo)
            fe.title(titulo)
            fe.link(href=link_completo)

        fg.rss_file('feed.xml')
        print("Arquivo feed.xml gerado!")

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    extrair_noticias()