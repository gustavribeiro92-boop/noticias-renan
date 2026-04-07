import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone, timedelta
import time

def extrair_noticias():
    # Configuração de fuso horário e anti-cache
    fuso_brasilia = timezone(timedelta(hours=-3))
    ts = int(time.time())
    url_alvo = f"https://www.camara-americana.sp.gov.br/Noticia/PaginaVereador/1?vereador=160&cache={ts}"
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
                # CORREÇÃO: Usar variáveis específicas para cada item dentro do loop
                titulo_noticia = tag_h4.get_text().strip() 
                url_noticia = base_url + tag_a['href'].strip() if tag_a['href'].startswith('/') else tag_a['href'].strip()
                img_noticia = base_url + tag_img['src'] if tag_img and tag_img.get('src') else ""
                data_texto = tag_p_data.get_text().strip() if tag_p_data else ""
                
                try:
                    data_obj = datetime.strptime(data_texto, '%d/%m/%Y').replace(tzinfo=fuso_brasilia)
                except:
                    data_obj = datetime.now(fuso_brasilia)

                noticias_lista.append({
                    'titulo': titulo_noticia,
                    'url': url_noticia,
                    'img': img_noticia,
                    'data': data_obj,
                    'data_str': data_texto
                })

        # Ordenar: Mais recentes primeiro
        noticias_lista.sort(key=lambda x: x['data'], reverse=True)

        fg = FeedGenerator()
        fg.id(url_alvo)
        fg.title('Notícias - Renan de Angelo')
        fg.link(href=url_alvo, rel='alternate')
        fg.link(href=link_rss_final, rel='self')
        fg.language('pt-br')
        fg.lastBuildDate(datetime.now(fuso_brasilia))

        for i, n in enumerate(noticias_lista):
            fe = fg.add_entry()
            fe.id(n['url'])
            fe.title(n['titulo'])
            fe.link(href=n['url'])
            
            # Garante que o WordPress entenda a ordem cronológica
            hora_prioridade = n['data'].replace(hour=23, minute=59 - (i % 60), second=0)
            fe.pubDate(hora_prioridade)
            
            # CORREÇÃO: A descrição agora usa n['titulo'] para ser exclusiva de cada post
            if n['img']:
                fe.enclosure(n['img'], 0, 'image/jpeg')
                fe.description(f'<img src="{n["img"]}" style="width:100%"/><br/>{n["data_str"]} - {n["titulo"]}')
            else:
                fe.description(f'{n["data_str"]} - {n["titulo"]}')

        fg.rss_file('feed.xml', pretty=True)
        print("Sucesso! O feed agora está com títulos e descrições individuais.")

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    extrair_noticias()
