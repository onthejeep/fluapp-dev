# For more information, please refer to https://aka.ms/vscode-docker-python
# FROM python:3.8-slim
# COPY --from=openjdk:slim / /

FROM python:3.8-slim
COPY --from=openjdk:8-jre-slim /usr/local/openjdk-8 /usr/local/openjdk-8

EXPOSE 5002

# Keeps Python from generating .pyc files in the container
ENV JAVA_HOME=/usr/local/openjdk-8
ENV DATABRICKS_AAD_TOKEN=dapiba8922c68bc5771452f29d3a5023037e
ENV COMPUTERNAME=SHUYANG

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

RUN export DATABRICKS_HOST=https://adb-157300333618041.1.azuredatabricks.net && \
    export DATABRICKS_API_TOKEN=dapiba8922c68bc5771452f29d3a5023037e && \
    export DATABRICKS_ORG_ID=157300333618041 && \
    export DATABRICKS_PORT=15001 && \
    export DATABRICKS_CLUSTER_ID=0301-025838-q6p5olwg && \
    echo "{\"host\": \"${DATABRICKS_HOST}\",\"token\": \"${DATABRICKS_API_TOKEN}\",\"cluster_id\":\"${DATABRICKS_CLUSTER_ID}\",\"org_id\": \"${DATABRICKS_ORG_ID}\", \"port\": \"${DATABRICKS_PORT}\" }" >> /root/.databricks-connect

ENV SPARK_HOME=/usr/local/lib/python3.8/site-packages/pyspark

RUN apt install git


WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
# RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
# USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:5002", "app:app"]
