import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone, timedelta
import time
from flask import Flask, Response

app = Flask(__name__)

# Essa linha cria a URL do seu feed
@app.route('/feed')
def gerar_feed():
    fuso_brasilia = timezone(timedelta(hours=-3))
    ts = int(time.time())
    url_alvo = f"https://www.camara-americana.sp.gov.br/Noticia/PaginaVereador/1?vereador=160&cachebuster={ts}"
    base_url = "https://www.camara-americana.sp.gov.br"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }

    try:
        response = requests.get(url_alvo, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        blocos = soup.find_all('div', class_='link-box')
        noticias_lista = []

        for bloco in blocos:
            tag_h4 = bloco.find('h4', class_='color-link')
            tag_a = bloco.find('a', href=True)
            tag_p_data = bloco.find('p', class_='color-link')

            if tag_h4 and tag_a:
                titulo = tag_h4.get_text(strip=True)
                link_final = base_url + tag_a['href'] if tag_a['href'].startswith('/') else tag_a['href']
                data_str = tag_p_data.get_text(strip=True)[-10:] if tag_p_data else ""
                
                try:
                    dt_obj = datetime.strptime(data_str, '%d/%m/%Y').replace(tzinfo=fuso_brasilia)
                except:
                    dt_obj = datetime.now(fuso_brasilia)

                noticias_lista.append({
                    'titulo': titulo,
                    'link': link_final,
                    'data_obj': dt_obj
                })

        noticias_lista.sort(key=lambda x: x['data_obj'], reverse=True)

        fg = FeedGenerator()
        fg.id(url_alvo)
        fg.title('Notícias - Renan de Angelo')
        fg.link(href=url_alvo, rel='alternate')
        fg.language('pt-br')
        fg.lastBuildDate(datetime.now(fuso_brasilia))

        for i, n in enumerate(noticias_lista):
            fe = fg.add_entry()
            fe.id(n['link']) 
            fe.title(n['titulo'])
            fe.link(href=n['link'])
            data_com_segundos = n['data_obj'].replace(hour=23, minute=59, second=60-i if i < 60 else 0)
            fe.pubDate(data_com_segundos)

        # A MÁGICA AQUI: Retorna o XML diretamente para quem acessar o link, sem salvar nada!
        xml_feed = fg.rss_str(pretty=True)
        return Response(xml_feed, mimetype='application/rss+xml')

    except Exception as e:
        return f"Erro ao gerar feed: {e}", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
