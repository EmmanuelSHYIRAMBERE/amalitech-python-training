FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
# --trusted-host: corporate SSL-intercepting proxy's CA isn't in this image's
# trust store, so pip's HTTPS verification to PyPI fails otherwise — same
# root cause as the app's own httpx.Client(verify=False) (see reflection.md).
RUN pip install --no-cache-dir \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    --trusted-host pypi.python.org \
    -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
