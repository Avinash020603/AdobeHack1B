FROM python:3.13


ENV PYTHONUNBUFFERED=1


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        cmake \
        pkg-config \
        libgl1-mesa-glx \
        libsm6 \
        libxrender-dev \
        libxext6 \
        && rm -rf /var/lib/apt/lists/*


RUN pip install --upgrade pip


COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt


WORKDIR /app


COPY . /app


VOLUME ["/app/input", "/app/output"]


CMD ["python", "main.py"]
