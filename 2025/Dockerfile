FROM nvidia/cuda:12.6.0-runtime-ubuntu22.04
RUN apt-get update && apt-get install -y wget bzip2 make

RUN wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/miniconda && \
    rm /tmp/miniconda.sh
ENV PATH="/opt/miniconda/bin:${PATH}"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY grab_raw_data.py .
COPY featurize_data.py .
COPY train_models.py .
COPY calibrate.py .
COPY get_win_percentages.py .
COPY play_bracket.py .
COPY Makefile .
CMD ["python", "train_models.py"]