# Diccionario de URLs de imágenes para moods comunes
mood_images = {
    'Acerbic': 'https://images.unsplash.com/photo-1546548970-71785318a17b?q=80&w=1974&auto=format&fit=crop',
    'Aggressive': 'https://images.unsplash.com/photo-1564166174574-a9666f590437?q=80&w=1974&auto=format&fit=crop',
    'Agreeable': 'https://images.unsplash.com/photo-1533041262434-c62a627ef0a2?q=80&w=2070&auto=format&fit=crop',
    'Airy': 'https://images.unsplash.com/photo-1607113734643-7e78f2f19f2b?q=80&w=1974&auto=format&fit=crop',
    'Ambitious': 'https://images.unsplash.com/photo-1593672715438-d88a70629abe?q=80&w=1974&auto=format&fit=crop',
    'Amiable/Good-Natured': 'https://images.unsplash.com/photo-1543807535-eceef0bc6599?q=80&w=1974&auto=format&fit=crop',
    'Angst-Ridden': 'https://images.unsplash.com/photo-1674156423391-a65ab2a435de?q=80&w=1974&auto=format&fit=crop',
    'Sad': 'https://images.unsplash.com/photo-1516585427167-9f4af9627e6c?w=500&h=500&fit=crop',
    'Anguished/Distraught':'https://images.unsplash.com/photo-1501719326211-cc2c472ebc9c?q=80&w=1978&auto=format&fit=crop',
    'Angular': 'https://images.unsplash.com/photo-1519642518514-f1a6d963547b?q=80&w=2008&auto=format&fit=crop',
    'Anthemic': 'https://merriam-webster.com/assets/mw/images/article/art-wap-landing-mp-lg/alt-5a2186a634509-4581-b345abf87a1d588f376144f4463a168d@1x.jpg',
    'Angry': 'https://images.unsplash.com/photo-1525785967371-87ba44b3e6cf?q=80&w=2073&auto=format&fit=crop',
    'Animated': 'https://images.unsplash.com/photo-1521669246297-b04a27e36f07?q=80&w=2070&auto=format&fit=crop',
    'Relaxing': 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=500&h=500&fit=crop',
    'Energetic': 'https://images.unsplash.com/photo-1535083153872-a199fb7650a5?w=500&h=500&fit=crop',
    'Romantic': 'https://images.unsplash.com/photo-1517857399767-a9b40d2c8a0f?w=500&h=500&fit=crop',
    'Epic': 'https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=500&h=500&fit=crop',
    'Melancholic': 'https://images.unsplash.com/photo-1504275107627-0c2ba7a43dba?w=500&h=500&fit=crop',
    'Dreamy': 'https://images.unsplash.com/photo-1507608869274-d3177c8bb4c7?w=500&h=500&fit=crop',
    'Dramatic': 'https://images.unsplash.com/photo-1595849884236-5697695cbb33?w=500&h=500&fit=crop',
    # Imagen predeterminada para moods que no están en la lista
    'default': 'https://images.unsplash.com/photo-1571330735066-03aaa9429d89?w=500&h=500&fit=crop'
}

def get_mood_image(mood_name):
    """
    Devuelve la URL de la imagen para un mood dado.
    Si el mood no está en el diccionario, devuelve la imagen predeterminada.
    """
    return mood_images.get(mood_name, mood_images['default'])