import json
from decimal import Decimal
from typing import Any
import requests

from common import PriceInfo, TokenOverview
from custom_exceptions import InvalidSolanaAddress, InvalidTokens, NoPositionsError

BIRDEYE_API_KEY= "451846c7a9bc440d933652aba468b9e9"


class Pubkey:
    pass

def is_solana_address(input_string: str) -> bool:
    try:
        Pubkey.from_string(input_string)
        return True

    except ValueError:
        return False
SOL_MINT = "So11111111111111111111111111111111111111112"


class APIError:
    pass


class DexScreenerClient:
    """
    Handler class to assist with all calls to DexScreener API
    """

    @staticmethod
    def _validate_token_address(token_address):
        """
        Validates token address to be a valid solana address

        Args:
            token_address (str): Token address to validate

        Returns:
            None: If token address is valid

        Raises:
            NoPositionsError: If token address is empty
            InvalidSolanaAddress: If token address is not a valid solana address
        """
        if not token_address:
            raise NoPositionsError("Token address cannot be empty")
        if len(token_address) == 44:
            return True
        else:
            raise InvalidSolanaAddress("Invalid Solana address format")

        return None

    def _validate_token_addresses(self, token_addresses: list[str]):
        """
        Validates token addresses to be a valid solana address

        Args:
            token_addresses (list[str]): Token addresses to validate

        Returns:
            None: If token addresses are valid

        Raises:
            NoPositionsError: If token addresses are empty
            InvalidSolanaAddress: If any token address is not a valid solana address
        """
        # Check if token_addresses is empty
        if not token_addresses:
            raise NoPositionsError("Token addresses list is empty")

        # Check each token address for validity
        for address in token_addresses:
            if not self._validate_token_addresses(address):
                raise InvalidSolanaAddress(f"Invalid Solana address: {address}")

    @staticmethod
    def _validate_response(resp: requests.Response):
        """
        Validates response from API to be 200

        Args:
            resp (requests.Response): Response from API

        Returns:
            None: If response is 200

        Raises:
            InvalidTokens: If response is not 200
        """
        if resp.status_code != 200:
            raise InvalidTokens()

    def _call_api(self, token_address: str) -> dict[str, Any]:
        """
        Calls DexScreener API for a single token

        Args:
            token_address (str): Token address for which to fetch data

        Returns:
            dict[str, Any]: JSON response from API

        Raises:
            InvalidTokens: If response is not 200
            NoPositionsError: If token address is empty
            InvalidSolanaAddress: If token address is not a valid solana address
        """
        # Check if the token address is empty
        if not token_address:
            raise NoPositionsError("Token address is empty.")

        # Check if the token address is a valid Solana address (You may need to implement a validation function)
        if not self._validate_token_address(token_address):
            raise InvalidSolanaAddress("Token address is not a valid Solana address.")

        # Make API request
        url = f"https://api.dexscreener.io/latest/dex/tokens/{token_address}"
        headers = {"x-api-key": "451846c7a9bc440d933652aba468b9e9"}  # Add your API key here
        response = requests.get(url, headers=headers)

        # Check if response is successful (status code 200)
        if response.status_code != 200:
            raise InvalidTokens("Response is not 200.")

        # Return JSON response
        return response.json()
        # print(response.json())

    def _call_api_bulk(self, token_addresses: list[str]) -> dict[str, Any]:
        """
            Calls DexScreener API for multiple tokens
            Args: token_addresses (list[str]): Token addresses for which to fetch data
            Returns: dict[str, Any]: JSON response from API
            Raises:InvalidTokens: If response is not 200 NoPositionsError: If token addresses are empty
    InvalidSolanaAddress: If any token address is not a valid solana address
            """
        if not token_addresses:
            raise NoPositionsError("Token addresses list is empty.")

        token_info_list = []

        for token_address in token_addresses:
            # Check if the token address is a valid Solana address (You may need to implement a validation function)
            if not self._validate_token_address(token_address):
                raise InvalidSolanaAddress(f"Token address '{token_address}' is not a valid Solana address.")

            # Make API request
            url = f"https://api.dexscreener.io/latest/dex/tokens/{token_address}"
            headers = {"x-api-key": "451846c7a9bc440d933652aba468b9e9"}  # Add your API key here
            response = requests.get(url, headers=headers)
            # Check if response is successful (status code 200)
            if response.status_code != 200:
                raise InvalidTokens(f"Response for token address '{token_address}' is not 200.")

            # Append token info to the list
            token_info_list.append(response.json())

        return token_info_list

    def fetch_prices_dex(self, token_addresses: list[str]) -> dict[str, PriceInfo[Decimal, Decimal]]:
        """
            For a list of tokens fetches their prices
            via multi API ensuring each token has a price
            Args:
                token_addresses (list[str]): A list of tokens for which to fetch prices
            Returns: dict[str, dict[Decimal, PriceInfo[str, Decimal]]: Mapping of token to a named tuple PriceInfo with price and liquidity in Decimal

            """
        if not token_addresses:
            raise NoPositionsError("Token addresses list is empty.")
        token_prices_usd = []
        for token_address in token_addresses:
            # Check if the token address is a valid Solana address (You may need to implement a validation function)
            if not self._validate_token_address(token_address):
                raise InvalidSolanaAddress(f"Token address '{token_address}' is not a valid Solana address.")

            url = f"https://api.dexscreener.io/latest/dex/tokens/{token_address}"
            headers = {"x-api-key": "451846c7a9bc440d933652aba468b9e9"}  # Add your API key here
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                # Parse the JSON content of the response
                data = response.json()

                # Access values from the dictionary
                pricevalue = data["pairs"][0]['priceUsd']
                liquidityval =  data["pairs"][0]['liquidity']
                # Do something with the value
                print("Price",pricevalue)
                print("Price",liquidityval)

            else:
                # If the request was not successful, print an error message
                print("Error:", response.status_code)

            if response.status_code != 200:
                raise InvalidTokens(f"Response for token address '{token_address}' is not 200.")

            # Extract priceUsd from response and append to token_prices_usd list
            token_info = response.json()
            price_usd = token_info.get('priceUsd')
            if price_usd:
                token_prices_usd.append(price_usd)

        return token_prices_usd
    def fetch_token_overview(self, address: str) -> TokenOverview:
        """
            For a token fetches their overview
            via Dex API ensuring each token has a price

            Args:
            address (str): A token address for which to fetch overview

            Returns:
            TokenOverview: Overview with a lot of token information I don't understand
            """


    @staticmethod
    def find_largest_pool_with_sol(token_pairs, address):
        max_entry = {}
        max_liquidity_usd = -1

        for entry in token_pairs:
            # Check if the baseToken address matches the specified address
            if entry.get("baseToken", {}).get("address") == address and entry["quoteToken"]["address"] == SOL_MINT:
                liquidity_usd = float(entry.get("liquidity", {}).get("usd", 0))
                if liquidity_usd > max_liquidity_usd:
                    max_liquidity_usd = liquidity_usd
                    max_entry = entry
        return max_entry

    token_address = [
        "WskzsKqEW3ZsmrhPAevfVZb6PuuLzWov9mJWZsfDePC",
        "2uvch6aviS6xE3yhWjVZnFrDw7skUtf6ubc7xYJEPpwj",
        "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
        "2LxZrcJJhzcAju1FBHuGvw929EVkX7R7Q8yA2cdp8q7b"
    ]

# test usage

your_instance = DexScreenerClient()
bulkresponse_data = your_instance._call_api_bulk(["EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm", "2uvch6aviS6xE3yhWjVZnFrDw7skUtf6ubc7xYJEPpwj"])
bulk_json = json.dumps(bulkresponse_data, indent=4)
print(bulk_json)

singleresponse_data= your_instance._call_api("EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm")
single_json = json.dumps(singleresponse_data, indent=4)
print("single API response", single_json)

token_addresses = ["EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm", "2uvch6aviS6xE3yhWjVZnFrDw7skUtf6ubc7xYJEPpwj"]
prices = your_instance.fetch_prices_dex(token_addresses)



















