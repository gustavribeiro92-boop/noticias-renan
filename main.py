import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime

def extrair_noticias():
    url_alvo = "https://www.camara-americana.sp.gov.br/Noticia/PaginaVereador/1?vereador=160"
    base_url = "https://www.camara-americana.sp.gov.br"
    link_rss_final = "https://raw.githubusercontent.com/gustavribeiro92-boop/noticias-renan/main/feed.xml"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(url_alvo, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        blocos_noticias = soup.find_all('div', class_='link-box')

        fg = FeedGenerator()
        fg.id(url_alvo)
        fg.title('Notícias - Renan de Angelo')
        fg.link(href=url_alvo, rel='alternate')
        fg.link(href=link_rss_final, rel='self')
        fg.description('Feed oficial de notícias da Câmara Municipal de Americana')
        fg.language('pt-br')

        for bloco in blocos_noticias:
            tag_h4 = bloco.find('h4', class_='color-link')
            tag_a = bloco.find('a', href=True)
            
            # Extração da Imagem
            tag_img = bloco.find('img')
            url_img = base_url + tag_img['src'] if tag_img and tag_img.get('src') else ""

            if tag_h4 and tag_a:
                titulo = tag_h4.get_text().strip()
                href = tag_a['href'].strip()
                url_completa = base_url + href if href.startswith('/') else href
                
                # Extração e formatação da Data para Ordem Cronológica
                tag_p_data = bloco.find('p', class_='color-link')
                data_texto = tag_p_data.get_text().strip() if tag_p_data else ""
                
                fe = fg.add_entry()
                fe.id(url_completa)
                fe.title(titulo)
                fe.link(href=url_completa)
                
                # Tenta converter a data (ex: 03/03/2026) para o formato que o RSS entende
                try:
                    data_obj = datetime.strptime(data_texto, '%d/%m/%Y')
                    fe.published(data_obj.replace(tzinfo=None))
                except:
                    pass

                # Insere a imagem para o Feedzy reconhecer
                if url_img:
                    fe.enclosure(url_img, 0, 'image/jpeg')
                    fe.description(f'<img src="{url_img}" style="width:100%" /><br/>{titulo}')
                else:
                    fe.description(f"Notícia oficial da Câmara de Americana - {data_texto}")

        fg.rss_file('feed.xml', pretty=True)
        print(f"Sucesso! {len(blocos_noticias)} notícias processadas com imagens.")

    except Exception as e:
        print(f"Erro no scraping: {e}")

if __name__ == "__main__":
    extrair_noticias()
