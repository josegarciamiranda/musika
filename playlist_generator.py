import os
import json
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError

BASE_MUSIC_FOLDER = "canciones"
DATA_FOLDER = "data"

def leer_tags(mp3_path):

    titulo = None
    artista = None

    try:
        audio = MP3(mp3_path)

        if audio.tags:

            if "TIT2" in audio.tags:
                titulo = audio.tags["TIT2"].text[0]

            if "TPE1" in audio.tags:
                artista = audio.tags["TPE1"].text[0]

    except ID3NoHeaderError:
        pass

    return titulo, artista


def generar_playlist(carpeta_playlist, output_json):

    canciones = []

    print("Escaneando:", carpeta_playlist)

    for root, _, files in os.walk(carpeta_playlist):

        for file in files:

            if not file.lower().endswith(".mp3"):
                continue

            full_path = os.path.join(root, file)

            titulo, artista = leer_tags(full_path)

            if not titulo:
                titulo = os.path.splitext(file)[0].replace("-", " ").replace("_"," ")

            if not artista:
                artista = "Artista Desconocido"

            # ruta relativa para la web
            ruta_relativa = os.path.relpath(full_path).replace("\\","/")

            canciones.append({
                "titulo": titulo.strip(),
                "artista": artista.strip(),
                "archivo": ruta_relativa
            })

    canciones.sort(key=lambda x: x["titulo"].lower())

    os.makedirs(os.path.dirname(output_json), exist_ok=True)

    with open(output_json,"w",encoding="utf-8") as f:
        json.dump(canciones,f,indent=2,ensure_ascii=False)

    print(f"{len(canciones)} canciones guardadas en {output_json}")


if __name__ == "__main__":

    playlists = [
        "espanol",
        "clasicos",
        "pop_actual"
    ]

    print("Generando playlists...\n")

    for playlist in playlists:

        carpeta = os.path.join(BASE_MUSIC_FOLDER, playlist)
        salida = os.path.join(DATA_FOLDER, f"{playlist}.json")

        generar_playlist(carpeta, salida)

    print("\nPlaylists generadas correctamente.")