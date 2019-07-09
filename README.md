**Dependencies:**

[Fapi-scrape](<https://gitlab.intes.by/dimao/fapi-scrape.git>)

**Usage:**

Settings stored in environment variables 

docker-compose.yml example:
```yaml
version: '2'
services:
  ftp_sync:
    container_name: ftp-sync
    image: registry.intes.by/dimao/ftp-sync:master
    environment:
      - USER=
      - PASSWORD=
      - SERVER=
      - CHECK_INTERVAL=5
    volumes:
      - /intes/import-ticket/tickets:/tickets
    restart: always
  
  pyticket:
    image: registry.intes.by/dimao/pyticket:v0.2.2
    container_name: import-ticket
    hostname: import-ticket
    environment:
      - WSDL_URL=http://10.0.7.8:8090/GnrtBT6NetWcfServiceLibrary.GnrtBT6NetWcfService/?wsdl
      - MON_FOLDER=/tickets  # Directory inside docker container
      - PROM_PORT=9090  # Prometheus endpoint port
      - HOST_NAME=http://fapi-scrape  # fapi-scrape service container name
      - PORT=8000  # fapi-scrape service container port
    volumes:
      - /intes/import-ticket/tickets:/tickets
      - /var/run/docker.sock:/docker.sock
    ports:
      - "9090:9090"
    depends_on:
      - ftp_sync
      - fapi-scrape
    restart: always

  fapi-scrape:
    image: registry.intes.by/dimao/fapi-scrape:v0.5.3
    container_name: fapi-scrape
    environment:
      - SITE_URL=https://fcbate.by/fan-zone
      - SCRAPE_TIME=20:00  # UTC
      - TIME_SHIFT=2
      - PORT=8000
    ports:
      - 8000:8000
    restart: always

```

