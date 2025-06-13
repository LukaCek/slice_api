FROM ubuntu:22.04

# Namestitev Python3, pip in zahtevanih knjižnic (vključno z libwebkit2gtk)
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    curl \
    libgl1 \
    libegl1 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libwebkit2gtk-4.0-37 \
    libjavascriptcoregtk-4.0-18 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    libglib2.0-0 \
    libdbus-1-3 \
    libwayland-client0 \
    libwayland-egl1 \
    && rm -rf /var/lib/apt/lists/*

# Nastavitev delovnega imenika
WORKDIR /app

# Prenos OrcaSlicer AppImage iz uradnega GitHub izida in nastavitev izvrševanja
RUN curl -L https://github.com/SoftFever/OrcaSlicer/releases/download/v2.3.0/OrcaSlicer_Linux_AppImage_V2.3.0.AppImage -o OrcaSlicer.AppImage \
    && chmod +x OrcaSlicer.AppImage \
    && ./OrcaSlicer.AppImage --appimage-extract \
    && ln -s /app/squashfs-root/AppRun /usr/local/bin/orcaslicer

# Namestitev Flask prek pip
RUN pip3 install Flask

# Kopiranje aplikacije in drugih datotek ter ustvarjanje začasne mape
RUN mkdir temp && mkdir -p /root/.config/OrcaSlicer
COPY all/ test_data/
COPY templates/ templates/
COPY app.py files/ ./

# Nastavitve okolja za Flask
ENV FLASK_APP=app.py
EXPOSE 8080

# Zagon Flask aplikacije
CMD ["python3", "app.py"]
