import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone, timedelta
import time

def extrair_noticias():
    fuso_brasilia = timezone(timedelta(hours=-3))
    # Anti-cache: gera um número diferente toda vez que o robô roda
    ts = int(time.time())
    url_alvo = f"https://www.camara-americana.sp.gov.br/Noticia/PaginaVereador/1?vereador=160&cachebuster={ts}"
    base_url = "https://www.camara-americana.sp.gov.br"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
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
                # Garante que o link seja completo
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

        # Ordenar: Recente no topo
        noticias_lista.sort(key=lambda x: x['data_obj'], reverse=True)

        fg = FeedGenerator()
        fg.id(url_alvo)
        fg.title('Notícias - Renan de Angelo')
        fg.link(href=url_alvo, rel='alternate')
        fg.language('pt-br')
        fg.lastBuildDate(datetime.now(fuso_brasilia))

        for i, n in enumerate(noticias_lista):
            fe = fg.add_entry()
            # O SEGREDO: O ID precisa ser o link. Se o ID mudar, o WordPress entende que é nova.
            fe.id(n['link']) 
            fe.title(n['titulo'])
            fe.link(href=n['link'])
            # Removemos a fe.description() conforme solicitado
            
            # Ajuste de segundos para garantir a ordem visual no site
            data_com_segundos = n['data_obj'].replace(hour=23, minute=59, second=60-i if i < 60 else 0)
            fe.pubDate(data_com_segundos)

        fg.rss_file('feed.xml', pretty=True)
        print(f"Sucesso! {len(noticias_lista)} notícias processadas.")

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    extrair_noticias()
