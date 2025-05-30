import shutil
from pathlib import Path
from typing import List, Dict, Union,BinaryIO
from uuid import UUID
import asyncio
from io import BytesIO
from urllib.parse import urlparse
import validators  
import requests
import os

async def exist_files():
    pass


async def save_files(
    files: List[Union[BinaryIO, str, Path]], 
    user_id: UUID,
    allowed_extensions: set = {'.pdf', '.docx', '.pptx', '.txt'}
) -> List[Dict[str, str]]:

    # Crear directorio base si no existe
    base_dir = Path("files") / str(user_id)
    base_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    for file in files:
        # Manejar tanto objetos de archivo como rutas
        if hasattr(file, 'read'):  # Es un objeto de archivo
            name = getattr(file, 'name', f"archivo_{len(results)}")
            content = file.read()
            file_is_path = False
        elif validators.url(str(file)):  # URL
            try:
                response = requests.get(file, stream=True)
                response.raise_for_status()
                name = os.path.basename(urlparse(file).path) or f"download{len(results)}"
                content = response.content
                origin = "url"
            except requests.RequestException as e:
                raise ValueError(f"Error al descargar {file}: {str(e)}")
        else:  # Es una ruta (str o Path)
            file_path = Path(file)
            name = file_path.name
            content = None
            file_is_path = True
        
        # Verificar extensión
        ext = Path(name).suffix.lower()
        if ext not in allowed_extensions:
            raise ValueError(f"Extensión no permitida: {ext}")
        
        # Ruta de destino
        destination = base_dir / name
        
        # Guardar el archivo según su tipo
        if file_is_path:
            shutil.copy2(file_path, destination)
        else:
            with open(destination, 'wb') as f:
                f.write(content)
            if hasattr(file, 'seek'):  # Rebobinar si es necesario
                file.seek(0)
        
        results.append({
            'name': name,
            'src': str(destination.absolute())
        })
    
    return results

archivo_memoria = BytesIO(b"contenido binario simulando docx")
archivo_memoria.name = "contrato.docx"  # Asignar nombre

files = [archivo_memoria,"https://www.colomos.ceti.mx/documentos/goe/los7HabitosGenteAltamenteEfectiva.pdf"]

asyncio.run(main=save_files(files=files,user_id="2d67ab6a-e49d-4fc3-b9ce-4dc1e592c820"))