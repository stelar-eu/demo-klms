FROM python:3.12-slim
#RUN apt-get update && apt-get install -y \
#    curl \
#    jq \
# && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app/
RUN pip install --no-cache-dir minio requests
RUN chmod +x run.sh
ENTRYPOINT ["python", "simple_tool.py"]
# ENTRYPOINT ["./run.sh"]
# CMD ["python", "simple_tool.py"]

