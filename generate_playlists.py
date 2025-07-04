import os
import json
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError, ID3

def generate_playlist_json_from_id3(playlist_folder_path, output_json_path, base_music_dir_name="canciones"):
    """
    Generates a JSON file for a music playlist by reading ID3 tags from MP3 files.

    Args:
        playlist_folder_path (str): The full path to the folder containing the MP3 files for a specific playlist (e.g., 'C:/path/to/your/project/canciones/espanol').
        output_json_path (str): The full path where the JSON file should be saved (e.g., 'C:/path/to/your/project/data/espanol.json').
        base_music_dir_name (str): The name of the root folder containing all playlist subfolders (e.g., 'canciones'). This is used to construct the 'archivo' path.
    """
    songs = []
    processed_count = 0
    error_count = 0

    playlist_name = os.path.basename(playlist_folder_path) # e.g., "espanol", "clasicos"

    if not os.path.isdir(playlist_folder_path):
        print(f"ERROR: La carpeta de la playlist no existe: {playlist_folder_path}")
        return

    print(f"Escaneando carpeta: {playlist_folder_path}")

    # Walk through the directory to find MP3s (handles subfolders if any, though usually not needed for simple playlists)
    for root, _, files in os.walk(playlist_folder_path):
        for file in files:
            if file.lower().endswith('.mp3'):
                full_mp3_path = os.path.join(root, file)
                processed_count += 1
                
                try:
                    audio = MP3(full_mp3_path, ID3=ID3) # Pass ID3 explicitly for robustness

                    # Get Title (TIT2) and Artist (TPE1) from ID3 tags
                    # Use .get() with a default to avoid KeyError if tag is missing
                    # .text[0] is needed because ID3 tags often return a list-like object
                    title = str(audio.get('TIT2', os.path.splitext(file)[0]))
                    artist = str(audio.get('TPE1', 'Artista Desconocido'))
                    
                    # Fallback if ID3 tags are empty or just whitespace
                    if not title.strip():
                        title = os.path.splitext(file)[0] # Use filename as fallback
                    if not artist.strip() or artist == 'None': # 'None' can appear if tag is truly empty
                        artist = "Artista Desconocido"

                    # Construct the relative path for the 'archivo' property in JSON
                    # This path is relative to the 'index.html' file's perspective.
                    # Example: "canciones/espanol/MiCancion.mp3"
                    # We need to ensure the path separator is '/' for web URLs
                    
                    # Calculate the path from base_music_dir_name onwards
                    # Example: C:/project/canciones/espanol/song.mp3 -> canciones/espanol/song.mp3
                    relative_path_from_base_music = os.path.relpath(full_mp3_path, os.path.join(os.path.dirname(os.path.dirname(output_json_path)), base_music_dir_name))
                    # Ensure forward slashes for web URLs
                    relative_path_for_json = relative_path_from_base_music.replace(os.sep, '/')

                    songs.append({
                        "titulo": title.strip(),
                        "artista": artist.strip(),
                        "archivo": relative_path_for_json
                    })
                    # print(f"  Procesado: '{title}' por '{artist}' -> '{relative_path_for_json}'") # Descomenta para ver cada canción procesada

                except ID3NoHeaderError:
                    print(f"  Advertencia: '{file}' no tiene etiquetas ID3. Usando el nombre del archivo para título/artista.")
                    title = os.path.splitext(file)[0].replace('_', ' ').replace('-', ' ').strip()
                    artist = "Artista Desconocido (sin ID3)"
                    # Fallback relative path construction
                    relative_path_from_base_music = os.path.relpath(full_mp3_path, os.path.join(os.path.dirname(os.path.dirname(output_json_path)), base_music_dir_name))
                    relative_path_for_json = relative_path_from_base_music.replace(os.sep, '/')
                    songs.append({
                        "titulo": title,
                        "artista": artist,
                        "archivo": relative_path_for_json
                    })
                    error_count += 1
                except Exception as e:
                    print(f"  ERROR al procesar '{file}': {e}")
                    error_count += 1

    # Sort songs alphabetically by title
    songs.sort(key=lambda x: x["titulo"].lower())

    try:
        # Create data folder if it doesn't exist
        os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(songs, f, indent=2, ensure_ascii=False)
        print(f"JSON '{output_json_path}' generado exitosamente con {len(songs)} canciones.")
    except Exception as e:
        print(f"ERROR: No se pudo guardar el JSON '{output_json_path}': {e}")


# --- CONFIGURACIÓN PRINCIPAL ---
if __name__ == "__main__":
    # Define la ruta base de tu proyecto. Asume que el script está en la misma carpeta que index.html
    # y las carpetas 'canciones' y 'data'.
    project_root = os.path.dirname(os.path.abspath(__file__))

    # Nombre de la carpeta donde están tus carpetas de playlists (ej: 'canciones' o 'music')
    # Este nombre debe coincidir con cómo accedes a tus MP3s desde index.html.
    # Si tus MP3s están directamente en el proyecto/espanol/, entonces esto sería ""
    # Pero lo más seguro es tener una carpeta principal como 'canciones'
    music_base_folder_name = "canciones"
    music_base_path = os.path.join(project_root, music_base_folder_name)

    # Carpeta donde se guardarán los archivos JSON generados.
    data_output_path = os.path.join(project_root, "data")

    # Lista de los nombres de tus carpetas de playlists (ej: 'espanol', 'clasicos', 'pop_actual')
    # ¡Asegúrate de que estos nombres coincidan EXACTAMENTE con los nombres de tus carpetas de MP3!
    playlists_to_process = [
        "espanol",
        "clasicos",
        "pop_actual",
        # Añade aquí todos los nombres de tus carpetas de playlists, una por línea:
        # "rock_clasico",
        # "bandas_sonoras",
        # "electronica",
        # "jazz",
        # "reguetton",
        # etc.
    ]

    print("--- Inicio del proceso de generación de playlists ---")

    for playlist_folder_name in playlists_to_process:
        playlist_full_path = os.path.join(music_base_path, playlist_folder_name)
        output_json_filename = f"{playlist_folder_name}.json" # Nombres de JSON: espanol.json, clasicos.json
        output_json_full_path = os.path.join(data_output_path, output_json_filename)

        print(f"\nProcesando playlist: '{playlist_folder_name}'...")
        generate_playlist_json_from_id3(playlist_full_path, output_json_full_path, music_base_folder_name)

    print("\n--- Proceso completado ---")
    print(f"Los archivos JSON se han guardado en la carpeta: {data_output_path}")