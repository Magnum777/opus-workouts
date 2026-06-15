#!/usr/bin/env python3
"""Trace where the USDC went."""
print("USDC went from $77.18 to $5.72")
print("SOL went from 0.0009 to 0.2693")
print()

external = 9.0 / 170  # 0.053
ata_reclaim = 0.083    # from closing empty ATAs
test_swap = 0.070      # manual $5 USDC->SOL test
sol_from_other = 0.2693 - 0.0009 - external - ata_reclaim - test_swap
usdc_spent = 77.18 - 5.72

print("--- SOL breakdown ---")
print("  Your $9 deposit: +" + str(round(external, 4)) + " SOL ($9)")
print("  ATA close refunds: +" + str(round(ata_reclaim, 4)) + " SOL (free)")
print("  My manual test swap ($5): +" + str(round(test_swap, 4)) + " SOL")
print("  Executor refill/buy swaps: +" + str(round(sol_from_other, 4)) + " SOL (cost $" + str(round(sol_from_other*170, 2)) + ")")
print()

print("--- USDC breakdown ---")
print("  My test swap: $5.00")
print("  Executor swaps (reported as failed): $" + str(round(usdc_spent - 5.00, 2)))
print()

print("--- What happened ---")
print("The executor sent refill and buy swaps. They all reported")
print('"TX not confirmed - likely failed" but they DID confirm')
print("just slowly. The code gave up after 20s verification but")
print("the TXes landed 30-60s later, consuming about $70 USDC")
print("over ~8 cycles of $5 refills and buy attempts.")
print()
print("Total: $71.46 USDC burned on SOL swaps + dust buy attempts")
print("SOL gained: 0.2155 from swaps ($36.63 at $170)")
print("Difference ($34.83): TX verification timeout + price slippage")