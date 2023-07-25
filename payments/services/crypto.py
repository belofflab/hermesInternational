from typing import Optional

import requests


class Crypto(object):
    def __init__(self, token: str) -> None:
        self.session = requests.Session()
        self.session.headers = {"Crypto-Pay-API-Token": token}

        self.api_url = "https://pay.crypt.bot/api/"

    def _send_request(self, method: str, url: str, data: Optional[dict] = None) -> dict:
        return self.session.request(method=method, url=self.api_url + url, json=data)

    def getMe(self) -> dict:
        return self._send_request("GET", "getMe")

    def createInvoice(self, asset: str, amount: str) -> dict:
        return self._send_request(
            "POST", "createInvoice", {"asset": asset, "amount": amount}
        ).json()


if __name__ == "__main__":
    crypto = Crypto(token="110981:AA3FManAQxim0xd6CNZF8zf1uzUIziDbe5d")
    print(crypto.createInvoice("USDT", "0"))
