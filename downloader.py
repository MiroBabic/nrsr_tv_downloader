import re
import requests
import os
import subprocess
import argparse
import shutil
import platform
import time

def extract_playlist_url(webpage_url):
    response = requests.get(webpage_url)
    if response.status_code == 200:
        page_content = response.text


        match = re.search(r'file: \'(//.*?\.m3u8)\'', page_content)
        if match:
            playlist_url = 'https:' + match.group(1)
            return playlist_url
        else:
            raise Exception("Playlist URL not found in the webpage source")
    else:
        raise Exception(f"Failed to load webpage: {webpage_url}")
    
def clear_output_folder(output_folder):
    if os.path.exists(output_folder):
        
        shutil.rmtree(output_folder)
    
    os.makedirs(output_folder)

def generate_filename_from_url(webpage_url):

    filename = re.sub(r'[^a-zA-Z0-9]', '_', webpage_url)
    
    return f"{filename}.mp4"

def download_m3u8(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to download m3u8 file: {url}")

def get_chunklist_url(m3u8_content, base_url):
    if platform.system() == "Windows":
        return get_chunklist_url_windows(m3u8_content, base_url)
    else:
        return get_chunklist_url_linux(m3u8_content, base_url)


def get_chunklist_url_linux(m3u8_content, base_url):
    for line in m3u8_content.splitlines():
        if line.endswith(".m3u8"):
            return os.path.join(base_url, line)
    raise Exception("Chunklist URL not found in the m3u8 file")


def get_chunklist_url_windows(m3u8_content, base_url):
    for line in m3u8_content.splitlines():
        if line.endswith(".m3u8"):
            return f"{base_url}/{line}".replace("\\", "/")
    raise Exception("Chunklist URL not found in the m3u8 file")


def get_chunk_urls(chunklist_content, base_url):
    chunk_urls = []
    for line in chunklist_content.splitlines():
        if line.endswith(".ts"):
            chunk_urls.append(os.path.join(base_url, line))
    return chunk_urls


def download_chunks_old(chunk_urls, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i, chunk_url in enumerate(chunk_urls):
        chunk_filename = f"chunk_{i}.ts"
        chunk_path = os.path.join(output_folder, chunk_filename)
        
        response = requests.get(chunk_url, stream=True)
        with open(chunk_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"Downloaded {chunk_filename}")

def download_chunks(chunk_urls, output_folder, max_retries=3):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    total_chunks = len(chunk_urls)

    for i, chunk_url in enumerate(chunk_urls):
        chunk_filename = f"chunk_{i}.ts"
        chunk_path = os.path.join(output_folder, chunk_filename)

        chunk_url = chunk_url.replace("\\", "/")

        for attempt in range(max_retries):
            try:
                response = requests.get(chunk_url, stream=True, timeout=10)
                response.raise_for_status()  

                with open(chunk_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:  
                            f.write(chunk)

                file_size = os.path.getsize(chunk_path)
                if file_size > 0:
                    print(f"\rDownloaded chunk {i+1}/{total_chunks} - Size: {file_size} bytes", end='', flush=True)
                    break  
                else:
                    raise ValueError(f"Chunk {chunk_filename} is 0 bytes")

            except (requests.exceptions.RequestException, ValueError) as e:
                print(f"\nError downloading {chunk_filename}: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying {chunk_filename} (Attempt {attempt + 1}/{max_retries})...")
                    time.sleep(2)  
                else:
                    print(f"Failed to download {chunk_filename} after {max_retries} attempts")

    print("\nDownload complete!")

def merge_chunks(output_folder, output_file):
    chunk_files = [f for f in os.listdir(output_folder) if f.endswith('.ts')]
    chunk_files = sorted(chunk_files, key=lambda x: int(re.search(r'(\d+)', x).group()))

    file_list_path = os.path.join(output_folder, "file_list.txt").replace("\\", "/")
    newline = '\r\n' if platform.system() == 'Windows' else '\n'
    with open(file_list_path, 'w', encoding='utf-8', newline=newline) as f:
        for chunk in chunk_files:
            chunk_full_path = os.path.abspath(os.path.join(output_folder, chunk)).replace("\\", "/")
            f.write(f"file '{chunk_full_path}'\n")

    ffmpeg_executable = None
    script_directory = os.path.dirname(os.path.abspath(__file__))  

    if platform.system() == "Windows":
        ffmpeg_executable = shutil.which("ffmpeg")
        
        if not ffmpeg_executable:
            ffmpeg_executable = os.path.join(script_directory, "ffmpeg.exe")
        else:
            ffmpeg_executable = os.path.abspath(ffmpeg_executable).replace("\\", "/")
    else:
        ffmpeg_executable = shutil.which("ffmpeg")

    if not ffmpeg_executable or not os.path.exists(ffmpeg_executable):
        raise Exception("ffmpeg not found! Please install ffmpeg or place ffmpeg.exe in the script directory.")

    file_list_path = os.path.abspath(file_list_path).replace("\\", "/")

    ffmpeg_cmd = [
        ffmpeg_executable,
        '-f', 'concat',
        '-safe', '0',
        '-i', file_list_path,
        '-c', 'copy',
        output_file
    ]

    #subprocess.run(ffmpeg_cmd, shell=(platform.system() == "Windows"))
    subprocess.run(ffmpeg_cmd)
    print(f"Video saved to {output_file}")

def main(webpage_url):
    playlist_url = extract_playlist_url(webpage_url)
    base_url = os.path.dirname(playlist_url)
    print(f"Extracted Playlist URL: {playlist_url}")

    
    output_folder = "chunks"
    clear_output_folder(output_folder)

    
    m3u8_content = download_m3u8(playlist_url)
    
    
    chunklist_url = get_chunklist_url(m3u8_content, base_url)
    print(f"Chunklist URL: {chunklist_url}")
    
    
    chunklist_content = download_m3u8(chunklist_url)
    chunk_urls = get_chunk_urls(chunklist_content, base_url)
    
    
    download_chunks(chunk_urls, output_folder)
    
    
    output_file = generate_filename_from_url(webpage_url)
    merge_chunks(output_folder, output_file)
    
    print("Download and merge complete!")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Download and merge video chunks from a webpage.")
    parser.add_argument('webpage_url', type=str, help='The URL of the webpage containing the video playlist')
    
    
    args = parser.parse_args()
    
    
    main(args.webpage_url)