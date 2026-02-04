# tezos mcp server

model context protocol server for tezos blockchain. lets claude interact with tezos natively through standard mcp tools.

## what it does

**read operations** (no keys needed)
- query balances, contract storage, transaction history
- get block info and network constants
- works across mainnet, shadownet, ghostnet

**write operations** (requires private key)
- send transactions and deploy contracts
- call contract entry points
- sign/verify messages, generate addresses

**networks supported**
- mainnet - production
- shadownet - primary testnet (recommended)
- ghostnet - legacy testnet (deprecated, migrate to shadownet)

## setup

### quick start (read-only)

works immediately without pytezos compilation:

```bash
python -m venv .venv
source .venv/bin/activate  # windows: .venv\Scripts\activate
pip install "mcp>=1.0.0" "httpx>=0.27.0"

# register with claude
claude mcp add --transport stdio tezos-readonly -- python server_readonly.py
```

### full setup (with transactions)

requires pytezos for write operations. on windows, easiest with conda:

```bash
conda create -n tezos-mcp python=3.11
conda activate tezos-mcp
pip install "mcp>=1.0.0" "httpx>=0.27.0"
conda install -c conda-forge pytezos

claude mcp add --transport stdio tezos -- python server.py
```

see `INSTALL_WINDOWS.md` for wsl2/docker options if conda isn't available.

## usage

```bash
claude
```

then:

```
> /mcp                                    # verify server connected
> what's the balance of tz1VSUr8... ?    # query balance
> show recent ops for tz1...             # transaction history
> latest block on shadownet               # block info
```

for transactions (requires TEZOS_PRIVATE_KEY env var):

```
> send 1 xtz to tz1... on shadownet
> deploy this contract to shadownet
> call mint on contract KT1...
```

### using the skill

```
> /tezos help me build an fa2 token
> /tezos optimize gas in this contract
> /tezos security checklist
```

## configuration

### environment variables

```bash
# private key for transactions
export TEZOS_PRIVATE_KEY="edsk..."

# optional: custom rpc nodes
export TEZOS_MAINNET_NODE="https://your-node.com"
export TEZOS_SHADOWNET_NODE="https://your-node.com"
```

or use `.env` file (see `.env.example`).

### default endpoints

verified from [teztnets.com](https://teztnets.com/) and official docs:

- mainnet: `https://mainnet.api.tez.ie`
- shadownet: `https://rpc.shadownet.teztnets.com`
- ghostnet: `https://rpc.ghostnet.teztnets.com`

## available tools

### read tools

| tool | params | example |
|------|--------|---------|
| get_balance | address, network | balance of tz1... on mainnet |
| get_contract_storage | contract_address, network | storage of KT1... |
| get_operations | address, limit, network | last 10 ops for tz1... |
| get_block_info | level (optional), network | latest block info |
| get_network_info | network | network constants |

### write tools

| tool | params | notes |
|------|--------|-------|
| send_transaction | destination, amount_mutez, network | requires private key |
| call_contract | contract, entry_point, params, amount | execute contract |
| originate_contract | code, storage, network | deploy new contract |
| sign_message | message | cryptographic signing |
| verify_signature | message, signature, pubkey | verify signed message |
| generate_address | mnemonic (optional) | create new address |

## examples

### check balance

```python
get_balance(
    address="tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb",
    network="mainnet"
)
```

### send transaction

```python
send_transaction(
    destination="tz1...",
    amount_mutez=1_000_000,  # 1 xtz
    network="shadownet"
)
```

### deploy contract

```python
originate_contract(
    code='<michelson_code>',
    storage='42',
    network="shadownet"
)
```

see `examples.md` for more patterns.

## project structure

```
tezos-mcp/
├── server.py              # full mcp server (13 tools)
├── server_readonly.py     # read-only version (4 tools)
├── pyproject.toml         # dependencies
├── README.md              # this file
├── QUICKSTART.md          # 5min setup guide
├── SOURCES.md             # verified endpoints & docs
├── examples.md            # usage patterns
├── INSTALL_WINDOWS.md     # windows installation
├── .env.example           # config template
└── .claude/
    └── skills/
        └── tezos/
            └── SKILL.md   # development guidance
```

## security

- never commit private keys
- use shadownet for testing
- audit contracts before mainnet deployment
- use environment variables for keys
- all endpoints verified against official sources

see `SOURCES.md` for documentation verification.

## resources

official documentation used:
- [tezos docs](https://docs.tezos.com/)
- [testnet registry](https://teztnets.com/)
- [tzkt api](https://api.tzkt.io/)
- [shadownet faucet](https://faucet.shadownet.teztnets.com/)
- [pytezos](https://pytezos.org/)
- [ligo](https://ligolang.org/)

## contributing

this implementation references official tezos documentation exclusively. all rpc endpoints and network configurations are verified against [teztnets.com](https://teztnets.com/) and [docs.tezos.com](https://docs.tezos.com/).

## license

mit
