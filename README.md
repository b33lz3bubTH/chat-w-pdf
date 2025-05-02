 docker run --name chatpdf-postgres   -e POSTGRES_USER=postgres   -e POSTGRES_PASSWORD=postgres   -e POSTGRES_DB=chatpdf   -p 5432:5432   -d postgres:latest


 docker run -d --name chromadb \
  -p 8000:8000 \
  chromadb/chroma