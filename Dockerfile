FROM python:3.12-slim

WORKDIR /code

RUN apt-get update \
    && apt-get install -y --no-install-recommends libexpat1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt

COPY config /code/config
COPY src /code/src
COPY services /code/services
COPY tests/fixtures /code/tests/fixtures

ENV PYTHONPATH=/code
ENV DATA_MODE=fixture

EXPOSE 8000

CMD ["uvicorn", "services.gateway.app:app", "--host", "0.0.0.0", "--port", "8000"]
