# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Needed for better experience in container terminal
ENV TERM=xterm-256color
ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:0
ENV QT_DEBUG_PLUGINS=1
# Add environment variables for WebEngine
ENV QTWEBENGINE_DISABLE_SANDBOX=1
ENV QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox"

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-pip \
        python3-dev \
        build-essential \
        libgl1 \
        libxcb1 \
        libxkbcommon0 \
        libdbus-1-3 \
        libegl1 \
        libopengl0 \
        libglx0 \
        libglvnd0 \
        fontconfig \
        libfontconfig1 \
        libxrender1 \
        libxcursor1 \
        libglib2.0-0 \
        libglib2.0-dev \
        libxcb-cursor0 \
        libxcb-xinerama0 \
        libxcb-randr0 \
        libxcb-shape0 \
        libxcb-render-util0 \
        libxcb-icccm4 \
        libxcb-keysyms1 \
        libxcb-image0 \
        x11-utils \
        libx11-xcb1 \
        libxcb-xkb1 \
        libxkbcommon-x11-0 \
        # Dependencies for QWebEngine
        libnss3 \
        libnspr4 \
        libxcomposite1 \
        libxdamage1 \
        libxrandr2 \
        libxtst6 \
        libasound2 \
        libatk1.0-0 \
        libatspi2.0-0 \
        libcups2 \
        libdrm2 \
        libxshmfence1 \
        libxss1 \
        # Vulkan support
        libvulkan1 \
        vulkan-tools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Set the working directory
WORKDIR /llm_gui

# Copy the application
COPY . .

# Run the application
CMD ["python", "main.py"]
