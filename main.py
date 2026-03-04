import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

def extrair_noticias():
    url_alvo = "https://www.camara-americana.sp.gov.br/Noticia/PaginaVereador/1?vereador=160"
    base_url = "https://www.camara-americana.sp.gov.br"
    link_rss_final = "https://raw.githubusercontent.com/gustavribeiro92-boop/noticias-renan/main/feed.xml"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(url_alvo, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Busca todos os links que contenham '/Noticia/Detalhe/' no endereço
        links_noticias = soup.find_all('a', href=lambda href: href and '/Noticia/Detalhe/' in href)

        fg = FeedGenerator()
        fg.id(url_alvo)
        fg.title('Noticias - Renan de Angelo')
        fg.link(href=url_alvo, rel='alternate')
        fg.link(href=link_rss_final, rel='self')
        fg.description('Feed de noticias do gabinete')
        fg.language('pt-br')

        # Usamos um set para evitar notícias duplicadas
        links_processados = set()

        for link_tag in links_noticias:
            href = link_tag['href'].strip()
            full_link = base_url + href if href.startswith('/') else href
            
            if full_link not in links_processados:
                # O título geralmente está dentro de um h3 ou é o próprio texto do link
                titulo = link_tag.get_text().strip()
                if not titulo or len(titulo) < 10: # Se o texto for curto, tenta buscar no h3 vizinho
                    parent = link_tag.find_parent()
                    h3 = parent.find('h3') if parent else None
                    titulo = h3.get_text().strip() if h3 else titulo

                if titulo and len(titulo) > 10:
                    fe = fg.add_entry()
                    fe.id(full_link)
                    fe.title(titulo)
                    fe.link(href=full_link)
                    fe.description(f"Noticia oficial do vereador Renan de Angelo - Americana/SP")
                    links_processados.add(full_link)

        fg.rss_file('feed.xml', pretty=True)
        print(f"Sucesso! {len(links_processados)} noticias encontradas.")

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    extrair_noticias()
