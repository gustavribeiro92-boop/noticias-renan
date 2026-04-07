import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone, timedelta
import time

def extrair_noticias():
    # 1. Configurações Iniciais
    fuso_brasilia = timezone(timedelta(hours=-3))
    ts = int(time.time())
    # URL com cachebuster para forçar dados novos
    url_alvo = f"https://www.camara-americana.sp.gov.br/Noticia/PaginaVereador/1?vereador=160&t={ts}"
    base_url = "https://www.camara-americana.sp.gov.br"
    link_github_raw = "https://raw.githubusercontent.com/gustavribeiro92-boop/noticias-renan/main/feed.xml"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Cache-Control': 'no-cache'
    }

    try:
        response = requests.get(url_alvo, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # O seletor correto baseado no seu HTML: blocos de notícia
        blocos = soup.find_all('div', class_='link-box')
        noticias_lista = []

        for bloco in blocos:
            # Captura o link e o título (estão dentro do h4)
            tag_h4 = bloco.find('h4', class_='color-link')
            tag_a = bloco.find('a', href=True)
            
            # Captura a imagem
            tag_img = bloco.find('img')
            
            # Captura a data (está no parágrafo com a classe color-link)
            tag_p_data = bloco.find('p', class_='color-link')

            if tag_h4 and tag_a:
                # Extração limpa dos dados
                titulo = tag_h4.get_text(strip=True)
                link = base_url + tag_a['href'] if tag_a['href'].startswith('/') else tag_a['href']
                img_url = base_url + tag_img['src'] if tag_img else ""
                data_str = tag_p_data.get_text(strip=True).replace(' ', '') if tag_p_data else ""
                
                # Tratamento da Data para ordenação
                try:
                    # Formato esperado: "01/04/2026"
                    data_limpa = data_str[-10:] # Pega os últimos 10 caracteres (a data)
                    dt_obj = datetime.strptime(data_limpa, '%d/%m/%Y').replace(tzinfo=fuso_brasilia)
                except:
                    dt_obj = datetime.now(fuso_brasilia)

                noticias_lista.append({
                    'titulo': titulo,
                    'link': link,
                    'img': img_url,
                    'data_obj': dt_obj,
                    'data_exibicao': data_limpa if 'data_limpa' in locals() else data_str
                })

        # 2. Ordenação: Mais recentes no topo
        noticias_lista.sort(key=lambda x: x['data_obj'], reverse=True)

        # 3. Geração do Feed RSS
        fg = FeedGenerator()
        fg.id(url_alvo)
        fg.title('Notícias - Renan de Angelo')
        fg.link(href=url_alvo, rel='alternate')
        fg.link(href=link_github_raw, rel='self')
        fg.description('Monitoramento oficial de notícias do gabinete')
        fg.language('pt-br')
        fg.lastBuildDate(datetime.now(fuso_brasilia))

        for i, n in enumerate(noticias_lista):
            fe = fg.add_entry()
            fe.id(n['link'])
            fe.title(n['titulo'])
            fe.link(href=n['link'])
            
            # Ajuste de pubDate para o WordPress não bugar a ordem (segundos diferentes)
            data_final = n['data_obj'].replace(hour=23, minute=59, second=60-i if i < 60 else 0)
            fe.pubDate(data_final)
            
            # Descrição com imagem e título único para cada item
            conteudo = f'<img src="{n["img"]}" style="width:100%; margin-bottom:10px;"/><br/><b>{n["data_exibicao"]}</b> - {n["titulo"]}'
            fe.description(conteudo)
            
            if n['img']:
                fe.enclosure(n['img'], 0, 'image/jpeg')

        # 4. Salva o arquivo
        fg.rss_file('feed.xml', pretty=True)
        print(f"Sucesso! {len(noticias_lista)} notícias processadas corretamente.")

    except Exception as e:
        print(f"Erro ao processar: {e}")

if __name__ == "__main__":
    extrair_noticias()
