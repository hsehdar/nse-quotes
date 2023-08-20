#!/usr/bin/env python3
import json
from nse import *

if __name__ == "__main__":

    nse = NSESession()

    print("Quote:\n", json.dumps(json.loads(nse.get_symbol_quote('CONCOR')), indent=2))
    print("\nHistory:\n", json.dumps(json.loads(nse.get_symbol_quote_history('CONCOR', '31-07-2023','18-08-2023')), indent=2))
