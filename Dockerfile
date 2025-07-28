
FROM python:3.10-slim


ENV PYTHONUNBUFFERED=1


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        libgl1-mesa-glx \
        libsm6 \
        libxrender-dev \
        libxext6 \
        && rm -rf /var/lib/apt/lists/*


WORKDIR /app


COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt


RUN python -c "import nltk; nltk.download('punkt')"


COPY . /app
RUN rm -rf /app/input /app/output  # Avoid overwrite of mounted folders


VOLUME ["/app/input", "/app/output"]


CMD ["python", "main.py"]
