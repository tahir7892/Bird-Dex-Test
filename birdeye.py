import requests


class BirdEyeClient:
    """
    Handler class to assist with all calls to BirdEye API
    """

    @property
    def _headers(self):
        return {
            "accept": "application/json",
            "x-chain": "solana",
            "X-API-KEY":  "451846c7a9bc440d933652aba468b9e9",
        }

    def _make_api_call(self, method: str, query_url: str, *args, **kwargs) -> requests.Response:
        match method.upper():
            case "GET":
                query_method = requests.get
            case "POST":
                query_method = requests.post
            case _:
                raise ValueError(f'Unrecognised method "{method}" passed for query - {query_url}')
        resp = query_method(query_url, *args, headers=self._headers, **kwargs)
        return resp

    def fetch_prices(token_addresses):
        """
        For a list of tokens fetches their prices
        via multi-price API ensuring each token has a price

        Args:
            token_addresses (list[str]): A list of tokens for which to fetch prices

        Returns:
           dict[str, dict[str, PriceInfo[Decimal, Decimal]]: Mapping of token to a named tuple PriceInfo with price and liquidity

        Raises:
            NoPositionsError: Raise if no tokens are provided
            InvalidToken: Raised if the API call was unsuccessful
        """
        api_url = "https://public-api.birdeye.so/public/multi_price?list_address=So11111111111111111111111111111111111111112"
        prices = {}

        # Construct the API URL with the list of token addresses
        url = api_url + "%2C".join(token_addresses)

        # Make a GET request to the API
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            for token_address in token_addresses:
                # Check if the token address has a corresponding price
                if token_address in data:
                    prices[token_address] = data[token_address]
                else:
                    prices[token_address] = None  # or any default value you prefer
        else:
            print("Failed to fetch data from the API:", response.status_code)

        return prices

    # Example usage
    token_addresses = [
        "WskzsKqEW3ZsmrhPAevfVZb6PuuLzWov9mJWZsfDePC",
        "2uvch6aviS6xE3yhWjVZnFrDw7skUtf6ubc7xYJEPpwj",
        "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm"
    ]

    prices = fetch_prices(token_addresses)
    for token_address, price in prices.items():
        print(f"Token: {token_address}, Price: {price}")



    def fetch_token_overview(self, address: str) -> TokenOverview:
        """
        For a token fetches their overview
        via multi-price API ensuring each token has a price

        Args:
            address (str): A token address for which to fetch overview

        Returns:
            dict[str, float | str]: Overview with a lot of token information I don't understand

        Raises:
            InvalidSolanaAddress: Raise if invalid solana address is passed
            InvalidToken: Raised if the API call was unsuccessful
       """
