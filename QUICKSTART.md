# quickstart

get running in 5 minutes.

## install

```bash
python -m venv .venv
source .venv/bin/activate  # windows: .venv\Scripts\activate
pip install "mcp>=1.0.0" "httpx>=0.27.0"
```

## register

```bash
claude mcp add --transport stdio tezos-readonly -- python server_readonly.py
claude mcp list  # verify connected
```

## test

```bash
claude
```

```
> /mcp
> what's the balance of tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb?
> show recent ops for tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb
> latest block on mainnet
```

## add transactions

need pytezos for write operations. easiest on windows with conda:

```bash
conda create -n tezos-mcp python=3.11
conda activate tezos-mcp
pip install "mcp>=1.0.0" "httpx>=0.27.0"
conda install -c conda-forge pytezos

# register full version
claude mcp add --transport stdio tezos -- python server.py

# set key for transactions
export TEZOS_PRIVATE_KEY="edsk..."
```

## get testnet xtz

shadownet faucet: https://faucet.shadownet.teztnets.com/

## common commands

```
balance of tz1... on shadownet
send 1 xtz to tz1... on shadownet
deploy this contract to shadownet
/tezos help with fa2 tokens
```

## resources

- [full readme](README.md)
- [examples](examples.md)
- [windows install](INSTALL_WINDOWS.md)
- [verified endpoints](SOURCES.md)
