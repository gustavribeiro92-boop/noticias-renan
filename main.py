import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import time

def extrair_noticias():
    timestamp = int(time.time())
    url_alvo = f"https://www.camara-americana.sp.gov.br/Noticia/PaginaVereador/1?vereador=160&cache={timestamp}"
    base_url = "https://www.camara-americana.sp.gov.br"
    link_rss_final = "https://raw.githubusercontent.com/gustavribeiro92-boop/noticias-renan/main/feed.xml"
    
    headers = {'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'}
    
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
                
                try:
                    data_obj = datetime.strptime(data_texto, '%d/%m/%Y')
                except:
                    data_obj = datetime.now()

                noticias_lista.append({
                    'titulo': titulo, 'url': url_completa, 'img': url_img, 'data': data_obj, 'data_str': data_texto
                })

        # Ordena: Mais recentes primeiro
        noticias_lista.sort(key=lambda x: x['data'], reverse=True)

        fg = FeedGenerator()
        fg.id(url_alvo)
        fg.title('Notícias - Renan de Angelo')
        fg.link(href=url_alvo, rel='alternate')
        fg.link(href=link_rss_final, rel='self')
        fg.language('pt-br')

        agora = datetime.now()
        for i, n in enumerate(noticias_lista):
            fe = fg.add_entry()
            fe.id(n['url'])
            fe.title(n['titulo'])
            fe.link(href=n['url'])
            
            # O TRUQUE: Soma a hora atual para o WordPress entender que é NOVO
            data_com_hora = n['data'].replace(hour=agora.hour, minute=agora.minute, second=agora.second)
            fe.pubDate(data_com_hora)
            
            if n['img']:
                fe.enclosure(n['img'], 0, 'image/jpeg')
                fe.description(f'<img src="{n["img"]}" style="width:100%"/><br/>{n["data_str"]} - {n["titulo"]}')
            else:
                fe.description(f'{n["data_str"]} - {n["titulo"]}')

        fg.rss_file('feed.xml', pretty=True)
        print("Sucesso! Ordem cronológica forçada.")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    extrair_noticias()
