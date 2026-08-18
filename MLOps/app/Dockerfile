FROM python:3.12-slim

WORKDIR /app

# libgomp1: runtime OpenMP (GNU) exigido pelo LightGBM.
# python:3.12-slim (Debian Bookworm) remove libgomp1 para minimizar tamanho;
# sem ela o linker falha com "libgomp.so.1: cannot open shared object file"
# ao importar qualquer extensão C++ compilada com -fopenmp.
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgomp1 && \
    rm -rf /var/lib/apt/lists/*

COPY MLOps/app/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "MLOps/app/app.py", "--server.address=0.0.0.0", "--server.fileWatcherType=none"]
