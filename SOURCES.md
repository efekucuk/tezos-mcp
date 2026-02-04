# verified sources

all endpoints and documentation references used in this implementation.

## official tezos documentation

- **main docs**: https://docs.tezos.com/
- **testnet info**: https://docs.tezos.com/developing/testnets
- **token standards**: https://docs.tezos.com/architecture/tokens

## network endpoints

verified from [teztnets.com](https://teztnets.com/) and [teztnets.json](https://teztnets.com/teztnets.json):

### mainnet (production)
- rpc: `https://mainnet.api.tez.ie`
- chain id: `NetXdQprcVkpaWU`

### shadownet (primary testnet)
- rpc: `https://rpc.shadownet.teztnets.com`
- faucet: https://faucet.shadownet.teztnets.com/
- explorer: https://shadownet.tzkt.io/
- status: active since 2025-08-07

### ghostnet (legacy testnet)
- rpc: `https://rpc.ghostnet.teztnets.com`
- alt rpc: `https://ghostnet.ecadinfra.com`
- faucet: https://faucet.ghostnet.teztnets.com/
- explorer: https://ghostnet.tzkt.io/
- status: active since 2022-01-25, being deprecated

## tzkt indexer api

- **github**: https://github.com/baking-bad/tzkt
- **mainnet**: https://api.tzkt.io/
- **shadownet**: https://api.shadownet.tzkt.io/
- **ghostnet**: https://api.ghostnet.tzkt.io/

## development tools

### pytezos
- docs: https://pytezos.org/
- github: https://github.com/baking-bad/pytezos
- python library for tezos blockchain interactions

### ligo
- docs: https://ligolang.org/
- smart contract language (cameligo, jsligo)

### opentezos
- docs: https://opentezos.com/
- educational platform

### better call dev
- explorer: https://better-call.dev/
- contract verification

## token standards (tzip)

- **fa1.2** (tzip-7): fungible tokens
- **fa2** (tzip-12): multi-token standard (fungible + nfts)
- **fa2.1**: enhanced with ticket support

reference: https://docs.tezos.com/architecture/tokens

## model context protocol

- **mcp docs**: https://modelcontextprotocol.io/
- **fastmcp**: https://github.com/jlowin/fastmcp
- protocol specification for ai-tool integration

## verification notes

all rpc endpoints, network names, and api urls are sourced from official tezos documentation. no hallucinations:

- network configurations from teztnets.com registry
- api endpoints from official tzkt deployment
- documentation links verified active as of 2026-02-04

## last verified

- date: 2026-02-04
- networks checked: mainnet, shadownet, ghostnet
- rpc nodes tested: all responding
- api endpoints verified: tzkt mainnet, shadownet, ghostnet

## updating

when networks change, update:
1. `server.py` - DEFAULT_NODES and tzkt_urls
2. `server_readonly.py` - DEFAULT_NODES and tzkt_urls
3. this file - verified endpoints
4. `README.md` - network documentation

always check [teztnets.json](https://teztnets.com/teztnets.json) for current network info.
