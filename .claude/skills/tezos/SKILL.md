---
name: tezos
description: Expert guidance for Tezos blockchain development, smart contracts, and operations. Use when working with Tezos blockchain, writing smart contracts in Michelson/LIGO, or performing blockchain operations.
user-invocable: true
allowed-tools: Read, Grep, Bash(npm *), Bash(ligo *), Bash(octez-client *)
---

# Tezos Blockchain Development Assistant

You are an expert Tezos blockchain developer. When working with Tezos:

## Smart Contract Development Best Practices

### Language Selection
- **Michelson**: Low-level stack-based language, use for maximum control and gas optimization
- **LIGO**: High-level language (CameLIGO, JsLIGO), recommended for most projects
- **SmartPy**: Python-based, great for rapid prototyping

### Security Checklist
1. **Reentrancy Protection**: Always update state before external calls
2. **Integer Overflow**: Use `mutez` and `nat` types appropriately
3. **Access Control**: Implement proper admin/owner checks
4. **Entry Point Validation**: Validate all parameters at entry point boundaries
5. **Storage Costs**: Minimize storage size to reduce deployment and operation costs
6. **Gas Limits**: Test operations to ensure they stay within gas limits

### Common Patterns

**Admin Pattern**:
```ligo
type storage = {
  admin: address;
  // other fields...
}

let check_admin (admin, sender : address * address) : unit =
  if admin <> sender then
    failwith "NOT_ADMIN"
  else ()
```

**Token Transfer Pattern**:
```ligo
let transfer (destination, amount, storage : address * tez * storage) : operation list * storage =
  let transfer_op = Tezos.transaction () amount (Tezos.get_contract_opt destination) in
  ([transfer_op], storage)
```

**Pausable Contract**:
```ligo
type storage = {
  paused: bool;
  // other fields...
}

let check_not_paused (paused : bool) : unit =
  if paused then failwith "CONTRACT_PAUSED" else ()
```

## Network Selection

- **Mainnet**: Production deployments only, costs real XTZ
- **Shadownet**: Primary testnet (recommended for all development and testing)
- **Ghostnet**: Legacy testnet (being deprecated - migrate existing projects to Shadownet)

**IMPORTANT**: Always test thoroughly on Shadownet before mainnet deployment!

See https://teztnets.com/ for current testnet information and faucets.

## Transaction Best Practices

1. **Amount Handling**: Always specify amounts in mutez (1 XTZ = 1,000,000 mutez)
2. **Gas Estimation**: Use simulation to estimate gas before sending
3. **Error Handling**: Parse Michelson error messages carefully
4. **Confirmation**: Wait for block confirmation before considering transaction final

## Storage Optimization

- Use `big_map` for large key-value stores (not included in context hash)
- Pack data when possible to reduce storage costs
- Avoid deeply nested structures
- Use `bytes` for efficient serialization

## Common Gotchas

1. **Mutez vs XTZ**: Always work in mutez internally, convert for display only
2. **Implicit Accounts**: tz1/tz2/tz3 addresses are implicit accounts, KT1 are contracts
3. **Entry Point Names**: Must match exactly (case-sensitive)
4. **Timestamps**: Use `Tezos.now` for block timestamp, not system time
5. **Randomness**: No native randomness, use commit-reveal or oracles

## Testing Strategy

1. **Unit Tests**: Test individual entry points with various inputs
2. **Integration Tests**: Test contract interactions
3. **Simulation**: Use `--dry-run` to test without committing
4. **Audit**: Get professional security audit for high-value contracts

## Gas Optimization Tips

- Minimize storage reads/writes
- Use views for read-only operations (no gas cost)
- Batch operations when possible
- Simplify Michelson code paths
- Avoid complex computations on-chain

## When Using Tezos MCP Tools

### Read Operations (No Key Required)
- `get_balance`: Check any address balance
- `get_contract_storage`: View contract state
- `get_operations`: Query transaction history
- `get_block_info`: Get block details
- `get_network_info`: Network information

### Write Operations (Require TEZOS_PRIVATE_KEY)
- `send_transaction`: Transfer XTZ
- `call_contract`: Execute contract entry point
- `originate_contract`: Deploy new contract
- `sign_message`: Sign arbitrary data

### Safety Reminders
- Always use testnet first (shadownet recommended)
- Never commit private keys to version control
- Use environment variables for sensitive data
- Double-check destination addresses
- Verify amounts before sending
- Get testnet XTZ from: https://faucet.shadownet.teztnets.com/

## FA2 Token Standard

When implementing FA2 (TZIP-12) tokens:

```ligo
type transfer = {
  from_: address;
  txs: transfer_destination list;
}

type transfer_destination = {
  to_: address;
  token_id: nat;
  amount: nat;
}
```

Key entry points:
- `transfer`: Move tokens between accounts
- `balance_of`: Query token balances
- `update_operators`: Manage transfer permissions

## Useful Resources

- Tezos Documentation: https://tezos.com
- LIGO Language: https://ligolang.org
- TzKT Explorer: https://tzkt.io
- Better Call Dev (Contract Explorer): https://better-call.dev
- OpenTezos Learning: https://opentezos.com

## Example Workflow

1. Write contract in LIGO
2. Compile to Michelson: `ligo compile contract contract.mligo`
3. Test on shadownet using MCP tools
4. Simulate operations: `octez-client run script ... --trace-stack`
5. Originate on testnet: Use `originate_contract` tool with `network="shadownet"`
6. Test thoroughly on shadownet
7. Audit code (professional security audit for production contracts)
8. Deploy to mainnet only after comprehensive testing

**Always prioritize security and testing over speed of deployment!**

## Token Standards (TZIP)

- **FA1.2** (TZIP-7): Fungible tokens only
- **FA2** (TZIP-12): Multi-token standard (fungible + NFTs)
- **FA2.1**: Enhanced with ticket support

See: https://docs.tezos.com/architecture/tokens
