import discord
from discord.ext import commands
import os
import requests
from unidecode import unidecode
import random
from datetime import datetime, timedelta
import asyncio
import time
from googleapiclient.discovery import build
import sqlite3
import unicodedata

# AUTORIZAÇÕES
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='-', intents=discord.Intents.all())

# Chave da API do YouTube
YOUTUBE_API_KEY = AI_apik

# Criação do cliente YouTube
youtube = build('youtube', 'v3', developerKey = YOUTUBE_API_KEY)

# Lista de IDs de playlists fixas
PLAYLISTS_FIXAS = [
    "PLWr4uRWd6xgAqEmGetVUlLJo-xSLEOUaz",  # Joshua Aaron
    "OLAK5uy_nYNMvR6Cy2MwBGurXcntDKW2-pvJl8AlU",  # Grupo Elo
    "OLAK5uy_no3F1Oaq8ziXzT16Ezuz_sqqoQqI2JHSY",   # Praise 4
    "OLAK5uy_mf1_0w2DUAvqymKJmluuNe2fUijPEwD5s", # Praise 5
    "OLAK5uy_mYWJaA_Pjps7f--t5aVxV9jN9JH4nYxGM", # Praise 7
    "PLmczvSV0WZ47uvS70C6cvy35RZtblRUZE", # Bob Fitts
    "PL8O2zIwxuu1C1OP9krsTXXaSnR799qgo9", # outras músicas
    "OLAK5uy_l3-EoBIiArAc7qJjeV1LhpDX4sb43Hw4M", # Vencedores por Cristo
    "PLzWjmBOf3rY3hAXmvMI1-W52a23u-3U4o" # harpa cristã
]

# Função para obter vídeos de uma playlist específica
def obter_videos_da_playlist(playlist_id):
    videos = []
    try:
        next_page_token = None
        while True:
            # Requisição para obter os vídeos da playlist
            playlist_response = youtube.playlistItems().list(
                playlistId=playlist_id,
                part="snippet",
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            videos.extend([
                {
                    "title": item["snippet"]["title"],
                    "videoId": item["snippet"]["resourceId"]["videoId"]
                }
                for item in playlist_response.get("items", [])
            ])

            # Verificar se há mais páginas de resultados
            next_page_token = playlist_response.get("nextPageToken")
            if not next_page_token:
                break
    except Exception as e:
        print(f"Erro ao buscar vídeos da playlist {playlist_id}: {e}")

    return videos

# Comando de música
@client.command()
async def musica(ctx):
    # Escolher uma playlist aleatória
    playlist_id = random.choice(PLAYLISTS_FIXAS)

    # Obter os vídeos da playlist escolhida
    videos = obter_videos_da_playlist(playlist_id)
    if not videos:
        await ctx.send("Não consegui encontrar vídeos na playlist escolhida. Tente novamente mais tarde.")
        return

    # Escolher um vídeo aleatório
    video = random.choice(videos)
    video_url = f"https://www.youtube.com/watch?v={video['videoId']}"
    video_title = video['title']

    # Enviar a música escolhida
    await ctx.send(f"Aqui está uma música aleatória da playlist escolhida:\n**{video_title}**\n{video_url}")

# Função para buscar múltiplos versículos (sempre em ALMEIDA) com controle de erro
def buscar_versiculos(referencias, tentativas=3):
    versiculos = []
    
    for referencia in referencias:
        tentativas_falhas = 0
        versiculo_encontrado = False
        
        while tentativas_falhas < tentativas:
            url = f"https://bible-api.com/{referencia}?translation=ALMEIDA"
            try:
                response = requests.get(url)
                
                if response.status_code == 200:
                    dados = response.json()
                    texto = dados.get("text", "")
                    if texto:
                        versiculos.append(f"{referencia}: {texto}")
                        versiculo_encontrado = True
                        break
                    else:
                        versiculos.append(f"Referência {referencia} não encontrada ou inválida.")
                        versiculo_encontrado = True
                        break
                else:
                    tentativas_falhas += 1
                    versiculos.append(f"Erro ao buscar {referencia}. Código de status: {response.status_code}. Tentando novamente...")
                    time.sleep(2)  # Pausa de 2 segundos antes da nova tentativa
            except requests.exceptions.RequestException as e:
                tentativas_falhas += 1
                versiculos.append(f"Erro de conexão ao buscar {referencia}: {e}. Tentando novamente...")
                time.sleep(2)  # Pausa de 2 segundos antes da nova tentativa
        
        if not versiculo_encontrado:
            versiculos.append(f"Não foi possível encontrar o versículo {referencia} após {tentativas} tentativas.")

    return versiculos

# Normalizar o nome do livro (minúsculas e sem acento)
def normalizar_livro(nome_livro):
    return unidecode(nome_livro.lower())

# Função para buscar versículos de forma ordenada
def versiculos_ordenados():
    livros = ["Gênesis", "Êxodo", "Levítico", "Números", "Deuteronômio", "Josué", "Juízes", "Rute", 
              "1 Samuel", "2 Samuel", "1 Reis", "2 Reis", "1 Crônicas", "2 Crônicas", "Esdras", "Neemias", 
              "Ester", "Jó", "Salmos", "Provérbios", "Eclesiastes", "Cânticos", "Isaías", "Jeremias", 
              "Lamentações", "Ezequiel", "Daniel", "Oseias", "Joel", "Amós", "Obadias", "Jonas", "Miqueias", 
              "Naum", "Habacuque", "Sofonias", "Ageu", "Zacarias", "Malaquias", "Mateus", "Marcos", "Lucas", 
              "João", "Atos", "Romanos", "1 Coríntios", "2 Coríntios", "Gálatas", "Efésios", "Filipenses", 
              "Colossenses", "1 Tessalonicenses", "2 Tessalonicenses", "1 Timóteo", "2 Timóteo", "Tito", 
              "Filemom", "Hebreus", "Tiago", "1 Pedro", "2 Pedro", "1 João", "2 João", "3 João", "Judas", "Apocalipse"]
    
    livro = random.choice(livros)
    capitulo_inicial = random.randint(1, 50)
    versiculo_inicial = random.randint(1, 20)

    versiculos = []
    for i in range(3):
        capitulo = capitulo_inicial
        versiculo = versiculo_inicial + i
        referencia = f"{livro} {capitulo}:{versiculo}"
        url = f"https://bible-api.com/{referencia}?translation=ALMEIDA"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                dados = response.json()
                texto = dados.get("text", "")
                versiculos.append(f"{referencia}: {texto}")
            else:
                versiculos.append(f"{referencia}: Versículo não encontrado.")
        except requests.exceptions.RequestException:
            versiculos.append(f"{referencia}: Erro de conexão.")
    
    return "\n\n".join(versiculos)

# Comando de versículo
@client.command()
async def versiculo(ctx, *, referencias: str):
    referencias = [ref.strip() for ref in referencias.split(",")]

    referencias_expandidas = []
    for referencia in referencias:
        if "-" in referencia:
            try:
                livro_capitulo, intervalo = referencia.split(" ", 1)
                livro_capitulo = normalizar_livro(livro_capitulo)
                capitulo, versiculos = intervalo.split(":")
                versiculo_inicial, versiculo_final = versiculos.split("-")

                for versiculo in range(int(versiculo_inicial), int(versiculo_final) + 1):
                    referencias_expandidas.append(f"{livro_capitulo} {capitulo}:{versiculo}")
            except ValueError:
                await ctx.send(f"Erro no formato da referência: {referencia}. Esperado formato: **'Livro Capítulo:Versículo'**.")
                return
        else:
            livro_capitulo = referencia.split(" ")[0]
            livro_capitulo = normalizar_livro(livro_capitulo)
            referencias_expandidas.append(referencia.replace(referencia.split(" ")[0], livro_capitulo))

    # Chamar a função de buscar os versículos
    versiculos = buscar_versiculos(referencias_expandidas)

    # Enviar os resultados
    for resultado in versiculos:
        await ctx.send(resultado)


# BUSCAR CAPÍTULO


# Função para buscar um capítulo ou livro no banco de dados
def buscar_capitulo_ou_livro(livro, capitulo=None):
    # Caminho para o arquivo do banco de dados
    db_path = "almeida_rc.sqlite"  # Ajuste conforme necessário

    # Dicionário para mapear os nomes dos livros aos seus IDs
    livros = {
        1: "Gênesis", 2: "Êxodo", 3: "Levítico", 4: "Números", 5: "Deuteronômio", 6: "Josué", 7: "Juízes", 8: "Rute", 9: "1 Samuel", 10: "2 Samuel", 11: "1 Reis", 12: "2 Reis", 13: "1 Crônicas", 14: "2 Crônicas", 15: "Esdras", 16: "Neemias", 17: "Ester", 18: "Jó", 19: "Salmos", 20: "Provérbios", 21: "Eclesiastes", 22: "Cânticos", 23: "Isaías", 24: "Jeremias", 25: "Lamentações", 26: "Ezequiel", 27: "Daniel", 28: "Oséias", 29: "Joel", 30: "Amós", 31: "Obadias", 32: "Jonas", 33: "Miqueias", 34: "Naum", 35: "Habacuque", 36: "Sofonias", 37: "Ageu", 38: "Zacarias", 39: "Malaquias", 40: "Mateus", 41: "Marcos", 42: "Lucas", 43: "João", 44: "Atos", 45: "Romanos", 46: "1 Coríntios", 47: "2 Coríntios", 48: "Gálatas", 49: "Efésios", 50: "Filipenses", 51: "Colossenses", 52: "1 Tessalonicenses", 53: "2 Tessalonicenses", 54: "1 Timóteo", 55: "2 Timóteo", 56: "Tito", 57: "Filemom", 58: "Hebreus", 59: "Tiago", 60: "1 Pedro", 61: "2 Pedro", 62: "1 João", 63: "2 João", 64: "3 João", 65: "Judas", 66: "Apocalipse"
    }

    # Inverter o dicionário para permitir busca pelo nome do livro
    nome_para_id = {nome.lower(): id for id, nome in livros.items()}

    # Verificar se o livro existe
    livro_id = nome_para_id.get(livro.lower())
    if not livro_id:
        return f"📖 Livro '{livro}' não encontrado. Verifique o nome e tente novamente."

    # Conectar ao banco de dados
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Consulta com ou sem capítulo
    if capitulo:
        query = "SELECT chapter, verse, text FROM Verses WHERE book = ? AND chapter = ?"
        cursor.execute(query, (livro_id, capitulo))
    else:
        query = "SELECT chapter, verse, text FROM Verses WHERE book = ?"
        cursor.execute(query, (livro_id,))

    # Buscar resultados
    resultados = cursor.fetchall()
    conn.close()

    # Verificar se há resultados
    if not resultados:
        return f"📖 Nenhum versículo encontrado para o livro '{livro}'{f' capítulo {capitulo}' if capitulo else ''}."

    # Formatar os resultados
    resposta = []
    for chapter, verse, text in resultados:
        resposta.append(f"📖 **{livro} {chapter}:{verse}** - {text}")

    return "\n".join(resposta)

# Comando para buscar um capítulo ou livro inteiro
@client.command()
async def capitulo(ctx, livro: str, capitulo: int = None):
    await ctx.send("🔍 Buscando no banco de dados...")
    try:
        resultado = buscar_capitulo_ou_livro(livro, capitulo)
        
        # Dividir o texto em partes menores para enviar no Discord
        partes = dividir_texto(resultado, limite=2000)  # Função divide texto maior que 2000 caracteres
        for parte in partes:
            await ctx.send(parte)
    except Exception as e:
        await ctx.send(f"⚠️ Ocorreu um erro ao realizar a busca: {e}")


# PESQUISA POR TEMA


# Dicionário que mapeia números dos livros para seus nomes
livros_dict = {
    1: "Gênesis", 2: "Êxodo", 3: "Levítico", 4: "Números", 5: "Deuteronômio",
    6: "Josué", 7: "Juízes", 8: "Rute", 9: "1 Samuel", 10: "2 Samuel",
    11: "1 Reis", 12: "2 Reis", 13: "1 Crônicas", 14: "2 Crônicas", 15: "Esdras",
    16: "Neemias", 17: "Ester", 18: "Jó", 19: "Salmos", 20: "Provérbios",
    21: "Eclesiastes", 22: "Cânticos", 23: "Isaías", 24: "Jeremias", 25: "Lamentações",
    26: "Ezequiel", 27: "Daniel", 28: "Oséias", 29: "Joel", 30: "Amós",
    31: "Obadias", 32: "Jonas", 33: "Miqueias", 34: "Naum", 35: "Habacuque",
    36: "Sofonias", 37: "Ageu", 38: "Zacarias", 39: "Malaquias", 40: "Mateus",
    41: "Marcos", 42: "Lucas", 43: "João", 44: "Atos", 45: "Romanos",
    46: "1 Coríntios", 47: "2 Coríntios", 48: "Gálatas", 49: "Efésios", 50: "Filipenses",
    51: "Colossenses", 52: "1 Tessalonicenses", 53: "2 Tessalonicenses", 54: "1 Timóteo",
    55: "2 Timóteo", 56: "Tito", 57: "Filemom", 58: "Hebreus", 59: "Tiago",
    60: "1 Pedro", 61: "2 Pedro", 62: "1 João", 63: "2 João", 64: "3 João",
    65: "Judas", 66: "Apocalipse"
}

# Função para normalizar texto (remover acentos e converter para minúsculas)
def normalizar_texto(texto):
    texto = unicodedata.normalize('NFD', texto)  # Decompor caracteres acentuados
    texto = ''.join(ch for ch in texto if unicodedata.category(ch) != 'Mn')  # Remover marcas de acento
    return texto.lower()  # Converter para minúsculas

# Função para buscar versículos por palavra-chave (somente palavras inteiras e normalizadas)
async def buscar_por_palavra_exata(palavra):
    db_path = "almeida_rc.sqlite"  # Caminho para o banco de dados

    # Normalizar a palavra-chave
    palavra_normalizada = normalizar_texto(palavra)

    # Conectar ao banco de dados
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Obter todos os versículos do banco de dados
    query = "SELECT book, chapter, verse, text FROM Verses"
    cursor.execute(query)
    resultados = cursor.fetchall()
    conn.close()

    # Filtrar os resultados localmente com a palavra-chave normalizada
    versiculos_filtrados = [
        (book, chapter, verse, text) 
        for book, chapter, verse, text in resultados 
        if palavra_normalizada in normalizar_texto(text)
    ]

    # Limitar a quantidade de versículos a 7
    versiculos_filtrados = versiculos_filtrados[:7]

    return versiculos_filtrados

# Função para dividir texto longo em partes menores (limite de 2000 caracteres por mensagem)
def dividir_texto(texto, limite=2000):
    partes = []
    while len(texto) > limite:
        # Encontrar o último '\n' antes do limite
        corte = texto.rfind("\n", 0, limite)
        if corte == -1:  # Não encontrou um '\n', cortar no limite
            corte = limite
        partes.append(texto[:corte])
        texto = texto[corte:]
    partes.append(texto)
    return partes

@client.command()
async def pesquisar(ctx, *, palavra: str):
    await ctx.send("🔍 Buscando no banco de dados...")

    try:
        versiculos_filtrados = await buscar_por_palavra_exata(palavra)

        # Se houver versículos filtrados, formatar a resposta
        if versiculos_filtrados:
            # Substituir o número do livro pelo nome no formato
            resposta = "\n".join(
                [f"📖 **{livros_dict.get(book, book)} {chapter}:{verse}** - {text}" 
                 for book, chapter, verse, text in versiculos_filtrados]
            )

            # Dividir a resposta em partes menores, respeitando o limite de 2000 caracteres
            partes = dividir_texto(resposta)

            # Enviar as partes no Discord
            for parte in partes:
                await ctx.send(parte)
        else:
            await ctx.send(f"Nenhum resultado encontrado para '{palavra}'.")
    
    except Exception as e:
        await ctx.send(f"⚠️ Ocorreu um erro ao realizar a busca: {e}")






# Evento de boas-vindas com embed
@client.event
async def on_member_join(member):
    channel_id = CHANNEL_ID
    channel = client.get_channel(channel_id)

    if channel:
        embed = discord.Embed(
            title="🎉 Bem-vindo(a) ao Bible Search!",
            description=(f"Olá, {member.mention}! Seja bem-vindo ao servidor **{member.guild.name}**! 😊\n\n"
                         "Confira abaixo algumas regras importantes para manter tudo organizado e divertido:"),
            color=0x00aaff
        )
        embed.add_field(
            name="📜 Regras do Servidor:",
            value=(
                "1️⃣ **Seja gentil e educado com todos;**\n"
                "2️⃣ **Evite spam ou links desnecessários;**\n"
                "3️⃣ **Use os canais nos temas certos;**\n"
                "4️⃣ **Compartilhe apenas conteúdos seguros e adequados;**\n"
                "5️⃣ **Respeite as diretrizes do Discord.**"
            ),
            inline=False
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        embed.set_footer(text=f"Agora somos {len(member.guild.members)} membros!")
        await channel.send(embed=embed)

# Comando para exibir as regras novamente
@client.command()
async def regras(ctx):
    embed = discord.Embed(
        title="Regras",
        description="Confira as regras para mantermos um ambiente saudável e divertido.",
        color=0x00aaff
    )
    embed.add_field(
        name="📜 Regras do Servidor:",
        value=( 
            "1️⃣ **Seja gentil e educado com todos;**\n"
            "2️⃣ **Evite spam ou links desnecessários;**\n"
            "3️⃣ **Use os canais nos temas certos;**\n"
            "4️⃣ **Compartilhe apenas conteúdos seguros e adequados;**\n"
            "5️⃣ **Respeite as diretrizes do Discord.**"
        ),
        inline=False
    )
    await ctx.send(embed=embed)

# Comando para exibir todos os comandos disponíveis (agora com o nome "ajuda")
@client.command()
async def ajuda(ctx):
    embed = discord.Embed(
        title="Comandos Disponíveis",
        description="Aqui estão todos os comandos que você pode usar.",
        color=0x00aaff
    )
    embed.add_field(
        name="-versiculo [referência] 📖",
        value="Retorna um ou mais versículos conforme a referência fornecida. Exemplo: '-versiculo João 3:16' ou '-versiculo Mateus 5:3-10'.",
        inline=False
    )
    embed.add_field(
        name="-capitulo [referência] 📖",
        value="Retorna um capítulo inteiro conforme a referência fornecida. Exemplo: '-versiculo Gênesis 1'.",
        inline=False
    )
    embed.add_field(
        name="-regras 📜",
        value="Exibe as regras do servidor para todos os membros conhecerem.",
        inline=False
    )
    embed.add_field(
        name="-ajuda ❔",
        value="Exibe todos os comandos disponíveis no bot.",
        inline=False
    )
    embed.add_field(
        name="-musica 🎶",
        value="Escolhe uma música aleatória de uma playlist aleatória da base de dados.",
        inline=False
    ) 
    embed.add_field(
        name="-pesquisar 🔍",
        value="Pesquise versículos por palavra-chave ou tema na base de dados da Bíblia.",
        inline=False
    ) 
    embed.add_field(
        name="Mensagem Diária 📫",
        value="O bot envia versículos aleatórios diariamente às 21h.",
        inline=False
    )
    
    await ctx.send(embed=embed)

# Evento on_ready com lógica para versículos diários
@client.event
async def on_ready():
    print(f"Conectado como {client.user}")
    
    # Configurar o horário para o evento diário (21h)
    channel_id = CHANNEL_ID
    channel = client.get_channel(channel_id)
    
    while True:
        agora = datetime.now()
        proximo_envio = agora.replace(hour=21, minute=0, second=0, microsecond=0)
        if agora >= proximo_envio:
            proximo_envio += timedelta(days=1)

        tempo_espera = (proximo_envio - agora).total_seconds()

        print(f"O robô está esperando para enviar a mensagem às {proximo_envio.strftime('%H:%M:%S')}.")
        await asyncio.sleep(tempo_espera)

        mensagem = versiculos_ordenados()
        await channel.send(f"📫 **Mensagem Diária:**\n\n{mensagem}")
        print("Mensagem enviada.")

# Configuração e execução do bot
client.run(BOT_TOKEN)
