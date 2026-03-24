"""Monkey patch for twikit's broken ClientTransaction (March 2026).

Twitter changed their JS bundle format on ~March 18, 2026.
twikit's regex no longer matches the new ondemand.s reference.
This patch fixes the regex and get_indices method.

See: https://github.com/d60/twikit/issues/408

This module MUST be imported BEFORE twikit is used.
"""

import re

_tx_mod = __import__(
    "twikit.x_client_transaction.transaction",
    fromlist=["ClientTransaction"],
)

_tx_mod.ON_DEMAND_FILE_REGEX = re.compile(
    r""",(\d+):["']ondemand\.s["']""", flags=(re.VERBOSE | re.MULTILINE)
)
_tx_mod.ON_DEMAND_HASH_PATTERN = r',{}:"([0-9a-f]{{1,}})"'


async def _patched_get_indices(self, home_page_response, session, headers):
    key_byte_indices = []
    response = self.validate_response(home_page_response) or self.home_page_response
    response_str = str(response)

    on_demand_file = _tx_mod.ON_DEMAND_FILE_REGEX.search(response_str)
    if on_demand_file:
        on_demand_file_index = on_demand_file.group(1)
        hash_regex = re.compile(
            _tx_mod.ON_DEMAND_HASH_PATTERN.format(on_demand_file_index)
        )
        hash_match = hash_regex.search(response_str)
        if hash_match:
            filename = hash_match.group(1)
            url = f"https://abs.twimg.com/responsive-web/client-web/ondemand.s.{filename}a.js"
            resp = await session.request(method="GET", url=url, headers=headers)
            matches = re.compile(r"\[(\d+)\],\s*16").finditer(str(resp.text))
            for item in matches:
                key_byte_indices.append(item.group(1))

    if not key_byte_indices:
        raise Exception("Couldn't get KEY_BYTE indices")

    key_byte_indices = list(map(int, key_byte_indices))
    return key_byte_indices[0], key_byte_indices[1:]


_tx_mod.ClientTransaction.get_indices = _patched_get_indices
