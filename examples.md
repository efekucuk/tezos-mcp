# usage examples

practical patterns for using the tezos mcp server.

## basic queries

### check balance

```
what's the balance of tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb on mainnet?
```

```python
get_balance(
    address="tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb",
    network="mainnet"
)
# returns: "Balance: 10,001.000000 XTZ"
```

### view contract storage

```
show me the storage of KT1GRSvLoikDsXujKgZPsGLX8k8VvR2Tq95b
```

```python
get_contract_storage(
    contract_address="KT1GRSvLoikDsXujKgZPsGLX8k8VvR2Tq95b",
    network="mainnet"
)
```

### transaction history

```
last 10 transactions for tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb on mainnet
```

```python
get_operations(
    address="tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb",
    limit=10,
    network="mainnet"
)
```

### block info

```
what's in the latest block on shadownet?
```

```python
get_block_info(network="shadownet")
# or specific block
get_block_info(level=1000000, network="mainnet")
```

## transactions

requires `TEZOS_PRIVATE_KEY` environment variable.

### send xtz

```
send 5 xtz to tz1abc... on shadownet
```

```python
send_transaction(
    destination="tz1abc...",
    amount_mutez=5_000_000,  # 5 xtz = 5M mutez
    network="shadownet"
)
```

### generate address

```
generate a new tezos address
```

```python
generate_address()
# returns address, public key, private key, mnemonic
# save the mnemonic securely
```

## smart contracts

### deploy contract

```
deploy a simple storage contract on shadownet initialized to 42
```

```python
originate_contract(
    code='[{"prim":"parameter","args":[{"prim":"int"}]},{"prim":"storage","args":[{"prim":"int"}]},{"prim":"code","args":[[{"prim":"CAR"},{"prim":"NIL","args":[{"prim":"operation"}]},{"prim":"PAIR"}]]}]',
    storage='42',
    network="shadownet",
    balance=0
)
```

### call contract

```
call the transfer entry point on KT1... with these params
```

```python
call_contract(
    contract_address="KT1...",
    entry_point="transfer",
    parameters='[{"from_": "tz1aaa", "txs": [{"to_": "tz1bbb", "token_id": 0, "amount": 100}]}]',
    amount=0,
    network="shadownet"
)
```

### mint nft

```
mint token id 1 to tz1... on contract KT1...
```

```python
call_contract(
    contract_address="KT1...",
    entry_point="mint",
    parameters='{"address": "tz1...", "token_id": 1, "metadata": {"": "ipfs://..."}}',
    amount=0,
    network="shadownet"
)
```

## workflows

### deploy and test token

```
1. deploy fa2 token contract to shadownet
2. mint 1000 tokens to my address
3. check my token balance
```

claude will:
- deploy contract with `originate_contract`
- mint tokens with `call_contract`
- verify with `get_contract_storage`

### check nft ownership

```
does tz1... own token 123 in contract KT1...?
```

claude will:
- query contract storage
- parse big_map for token ownership
- return yes/no with details

### compare networks

```
compare block height of mainnet vs shadownet
```

```python
# parallel queries
get_block_info(network="mainnet")
get_block_info(network="shadownet")
```

## using the skill

### smart contract development

```
/tezos help me build an escrow contract
```

skill provides:
- security best practices
- escrow pattern examples
- testing strategy

### gas optimization

```
/tezos this contract uses too much gas, optimize it
```

skill analyzes and suggests:
- reduce storage reads/writes
- simplify michelson paths
- use views for read-only ops

### fa2 implementation

```
/tezos implement fa2 nft collection with 10k items
```

skill provides:
- fa2 standard guidance
- efficient storage patterns (big_map)
- batch minting implementation
- tzip-21 metadata

## environment setup

### development

```bash
# .env
TEZOS_PRIVATE_KEY=edsk...testkey...
TEZOS_SHADOWNET_NODE=https://rpc.shadownet.teztnets.com
```

### production

```bash
# .env.production (never commit)
TEZOS_PRIVATE_KEY=edsk...prodkey...
TEZOS_MAINNET_NODE=https://mainnet.api.tez.ie
```

load environment:

```bash
source .env  # development
# or
source .env.production  # production (careful!)
```

## tips

### always test on testnet first

```
bad:  "deploy this to mainnet"
good: "deploy this to shadownet, test it, then deploy to mainnet"
```

### be explicit about networks

```
bad:  "balance of tz1..." (defaults to mainnet)
good: "balance of tz1... on shadownet"
```

### verify amounts

```
user: send 1000 xtz to tz1...
claude: that's 1000 xtz (1B mutez). confirm before i proceed.
```

### check storage before calling

```
user: call the swap entry point
claude: let me check contract storage first to understand state...
```

## sample addresses

### mainnet

- `tz1VSUr8wwNhLAzempoch5d6hLRiTh8Cjcjb` - tezos foundation (has balance)
- `KT1GRSvLoikDsXujKgZPsGLX8k8VvR2Tq95b` - plenty defi contract

### shadownet

get from faucet: https://faucet.shadownet.teztnets.com/

## troubleshooting

### private key not working

```bash
# verify format (starts with edsk/spsk/p2sk)
echo $TEZOS_PRIVATE_KEY

# or check .env
cat .env
```

### rpc connection timeout

```bash
# test connection
curl https://mainnet.api.tez.ie/chains/main/blocks/head/header

# try alternative
export TEZOS_MAINNET_NODE="https://rpc.tzbeta.net"
```

### gas limit exceeded

claude will:
- analyze operation
- suggest breaking into smaller ops
- recommend gas optimization
- use `/tezos` skill for optimization
