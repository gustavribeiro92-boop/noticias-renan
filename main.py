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
        
        blocos = soup.find_all('div', class_='link-box')
        noticias_lista = []

        for bloco in blocos:
            tag_h4 = bloco.find('h4', class_='color-link')
            tag_a = bloco.find('a', href=True)
            tag_img = bloco.find('img')
            tag_p_data = bloco.find('p', class_='color-link')
            
            if tag_h4 and tag_a:
                titulo = tag_h4.get_text().strip()
                url_completa = base_url + tag_a['href'].strip() if tag_a['href'].startswith('/') else tag_a['href'].strip()
                url_img = base_url + tag_img['src'] if tag_img and tag_img.get('src') else ""
                data_texto = tag_p_data.get_text().strip() if tag_p_data else ""
                
                # Transformamos o texto (ex: 03/03/2026) em data real para o Python ordenar
                try:
                    data_obj = datetime.strptime(data_texto, '%d/%m/%Y')
                except:
                    data_obj = datetime.now()

                noticias_lista.append({
                    'titulo': titulo,
                    'url': url_completa,
                    'img': url_img,
                    'data': data_obj,
                    'data_str': data_texto
                })

        # --- O SEGREDO DA ORDEM CRONOLÓGICA ---
        # Ordena a lista do maior para o menor (True = Recente Primeiro)
        noticias_lista.sort(key=lambda x: x['data'], reverse=True)

        fg = FeedGenerator()
        fg.id(url_alvo)
        fg.title('Notícias - Renan de Angelo')
        fg.link(href=url_alvo, rel='alternate')
        fg.link(href=link_rss_final, rel='self')
        fg.description('Feed oficial de notícias do gabinete')
        fg.language('pt-br')

        for n in noticias_lista:
            fe = fg.add_entry()
            fe.id(n['url'])
            fe.title(n['titulo'])
            fe.link(href=n['url'])
            # Garante que o RSS informe a data correta para o WordPress
            fe.published(n['data'].replace(tzinfo=None))
            
            if n['img']:
                fe.enclosure(n['img'], 0, 'image/jpeg')
                # Aspas duplas externas para evitar o erro de sintaxe anterior
                fe.description(f'<img src="{n["img"]}" style="width:100%"/><br/>{n["data_str"]} - {n["titulo"]}')
            else:
                fe.description(f'{n["data_str"]} - {n["titulo"]}')

        fg.rss_file('feed.xml', pretty=True)
        print(f"Sucesso! {len(noticias_lista)} notícias processadas e ordenadas.")

    except Exception as e:
        print(f"Erro no processamento: {e}")

if __name__ == "__main__":
    extrair_noticias()
