# windows installation

pytezos requires native C extensions. on windows, you have options.

## option 1: conda (recommended)

easiest approach with pre-built packages:

```bash
# install miniconda from https://docs.conda.io/en/latest/miniconda.html

conda create -n tezos-mcp python=3.11
conda activate tezos-mcp
pip install "mcp>=1.0.0" "httpx>=0.27.0"
conda install -c conda-forge pytezos

# register
claude mcp add --transport stdio tezos -- python server.py
```

## option 2: wsl2

use linux subsystem for native build:

```bash
# in wsl2 ubuntu
sudo apt-get update
sudo apt-get install -y build-essential libgmp-dev libsecp256k1-dev libsodium-dev python3-venv

python3 -m venv .venv
source .venv/bin/activate
pip install "mcp>=1.0.0" "pytezos>=3.11.0" "httpx>=0.27.0"

claude mcp add --transport stdio tezos -- python server.py
```

## option 3: docker

cross-platform container approach:

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libgmp-dev \
    libsecp256k1-dev \
    libsodium-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml server.py ./
RUN pip install --no-cache-dir "mcp>=1.0.0" "pytezos>=3.11.0" "httpx>=0.27.0"

CMD ["python", "server.py"]
```

```bash
docker build -t tezos-mcp .
docker run -it tezos-mcp
```

## option 4: read-only mode

if you just need queries (no transactions):

```bash
python -m venv .venv
.venv\Scripts\activate
pip install "mcp>=1.0.0" "httpx>=0.27.0"

# use read-only server
claude mcp add --transport stdio tezos-readonly -- python server_readonly.py
```

## troubleshooting

### error: microsoft visual c++ 14.0 required

install visual c++ build tools from:
https://visualstudio.microsoft.com/visual-cpp-build-tools/

select "desktop development with c++"

### error: fastecdsa build failed

expected on windows without build tools. use conda, wsl2, or read-only mode.

### verification

```bash
# test pytezos import
python -c "import pytezos; print('success')"

# check dependencies
pip list | findstr "mcp pytezos httpx"

# verify server
claude mcp list
```

## conda path for registration

if using conda, use full python path:

```bash
# windows
claude mcp add --transport stdio tezos -- C:\Users\YourName\miniconda3\envs\tezos-mcp\python.exe server.py

# or activate conda first
conda activate tezos-mcp
claude mcp add --transport stdio tezos -- python server.py
```
