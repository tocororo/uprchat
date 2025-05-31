import shutil
import base64
from pathlib import Path
from typing import List, Dict, Union, BinaryIO
from uuid import UUID
import validators
from urllib.parse import urlparse
import requests
import os
from io import BytesIO
from PIL import Image
import re
import asyncio


async def save_files(
    files: List[Union[BinaryIO, str, Path]], 
    user_id: UUID,
    allowed_extensions: set = {'.pdf', '.docx', '.pptx', '.txt', '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'},
    max_image_size: tuple = (1920, 1080),
    quality: int = 85
) -> List[Dict[str, str]]:
    """
    Guarda archivos e imágenes (incluyendo base64 y URLs de imágenes) en el directorio del usuario.
    
    Args:
        files: Lista de archivos (objetos file, paths, URLs o strings base64)
        user_id: ID del usuario para crear directorio
        allowed_extensions: Extensiones permitidas
        max_image_size: Tamaño máximo para redimensionar imágenes
        quality: Calidad para imágenes comprimidas
    
    Returns:
        Lista de diccionarios con información de cada archivo guardado
    """
    # Crear directorio base si no existe
    base_dir = Path("files") / str(user_id)
    base_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    
    for file in files:
        try:
            file_info = {
                'name': '',
                'src': '',
                'type': 'document',
                'origin': '',
                'success': True,
                'error': None
            }
            
            content = None
            filename = f"file_{len(results)}"
            file_is_path = False
            is_image = False
            
            # Manejar diferentes tipos de entrada
            if hasattr(file, 'read'):  # Objeto de archivo (BinaryIO)
                content = file.read()
                filename = getattr(file, 'name', filename)
                file_info['origin'] = 'binary'
                
                if hasattr(file, 'seek'):
                    file.seek(0)
                    
            elif isinstance(file, (str, Path)) and validators.url(str(file)):  # URL
                try:
                    # Primero hacemos HEAD request para verificar content-type
                    head_response = requests.head(file, allow_redirects=True)
                    content_type = head_response.headers.get('content-type', '')
                    
                    # Verificar si es imagen por extensión o content-type
                    url_path = urlparse(file).path
                    ext = Path(url_path).suffix.lower()
                    is_image_url = (ext in image_extensions) or content_type.startswith('image/')
                    
                    # Descargar contenido
                    response = requests.get(file, stream=True)
                    response.raise_for_status()
                    content = response.content
                    
                    # Determinar nombre de archivo
                    if ext in image_extensions:
                        filename = os.path.basename(url_path) or f"image_{len(results)}{ext}"
                    else:
                        filename = os.path.basename(url_path) or filename
                        
                        # Si es imagen por content-type pero no por extensión
                        if is_image_url and not ext:
                            ext = '.' + content_type.split('/')[-1]
                            if ext == '.jpeg':
                                ext = '.jpg'
                            filename = f"image_{len(results)}{ext}"
                    
                    file_info['origin'] = 'url'
                    is_image = is_image_url
                    
                except requests.RequestException as e:
                    raise ValueError(f"Error al descargar {file}: {str(e)}")
                    
            elif isinstance(file, str) and file.startswith('data:image'):  # Base64 image
                match = re.match(r'data:image/(\w+);base64,(.*)', file)
                if not match:
                    raise ValueError("Formato base64 no válido")
                
                img_type, b64_data = match.groups()
                ext = f'.{img_type}' if img_type != 'jpeg' else '.jpg'
                content = base64.b64decode(b64_data)
                filename = f"image_{len(results)}{ext}"
                file_info['origin'] = 'base64'
                is_image = True
                
            elif isinstance(file, (str, Path)):  # Ruta local
                file_path = Path(file)
                filename = file_path.name
                file_is_path = True
                file_info['origin'] = 'local'
            
            # Verificar extensión
            ext = Path(filename).suffix.lower()
            if ext not in allowed_extensions:
                raise ValueError(f"Extensión no permitida: {ext}")
            
            # Actualizar tipo de archivo
            if is_image or ext in image_extensions:
                file_info['type'] = 'image'
                is_image = True
            
            # Ruta de destino
            destination = base_dir / filename
            file_info['name'] = filename
            file_info['src'] = str(destination.absolute())
            
            # Guardar según el tipo y origen
            if file_is_path:
                if is_image:
                    img = Image.open(file_path)
                    img.thumbnail(max_image_size, Image.Resampling.LANCZOS)
                    img.save(destination, quality=quality)
                else:
                    shutil.copy2(file_path, destination)
            else:
                if is_image:
                    # Guardar imagen binaria (de URL o base64)
                    with open(destination, 'wb') as f:
                        f.write(content)
                    
                    # Procesar la imagen (redimensionar)
                    try:
                        img = Image.open(destination)
                        img.thumbnail(max_image_size, Image.Resampling.LANCZOS)
                        img.save(destination, quality=quality)
                    except Exception:
                        pass
                else:
                    # Guardar archivo binario normal
                    with open(destination, 'wb') as f:
                        f.write(content)
            
            results.append(file_info)
            
        except Exception as e:
            error_info = {
                'name': filename,
                'src': '',
                'type': '',
                'origin': file_info.get('origin', 'unknown'),
                'success': False,
                'error': str(e)
            }
            results.append(error_info)
    
    return results


# Testing the function
archivo_memoria = BytesIO(b"contenido binario simulando docx")
archivo_memoria.name = "contrato.docx" 

image = "data:image/jpeg;base64,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"

files = [archivo_memoria,"https://www.colomos.ceti.mx/documentos/goe/los7HabitosGenteAltamenteEfectiva.pdf",image]

asyncio.run(main=save_files(files=files,user_id="2d67ab6a-e49d-4fc3-b9ce-4dc1e592c820"))
