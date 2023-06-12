# locale

This is the repository for the research paper "A new Token Management System for Local Communities" by Fadi Barbàra, Flavia Fredda, Claudio Schifanella

## Installation

```bash
$ git clone https://github.com/disnocen/locale/
$ cd locale
$ npm install && pip install -r requisites.txt
```

## Steps for ganache

start ganache with the utility `ganache`

```bash
$ chmod +x ganache
$ ./ganache &
```

## Steps for IPFS

These are the steps for sending data to IPFS. Note that the instructions from
the [main
site](https://docs.ipfs.tech/quickstart/publish_cli/#install-and-register-to-w3)
are wrong. lack of `register` step. Se below the correct execution.

```bash
$ npm install -g @web3-storage/w3cli
$ w3 authorize <your@email.com>
$ w3 space create Pictures
$ w3 space register --email <your@email.com>
$ w3 up welcome-to-IPFS.jpg
```

## Run

```bash
python3 main.py
```

## Troubleshooting

If you use LibreSSL instead of OpenSSL you may have an error with `urllib3` when sending transactions.

One (dirty) way to solve it is to go into `$HOME/.local/lib/python3.10/site-packages/urllib3` and comment the lines in the `else` part in `__init__.py`:

```python3
# Ensure that Python is compiled with OpenSSL 1.1.1+
# If the 'ssl' module isn't available at all that's
# fine, we only care if the module is available.
try:
    import ssl
except ImportError:
    pass
else:
    # fmt: off
    # if (
    #     not ssl.OPENSSL_VERSION.startswith("OpenSSL ")
    #     or ssl.OPENSSL_VERSION_INFO < (1, 1, 1)
    # ):  # Defensive:
    #     raise ImportError(
    #         "urllib3 v2.0 only supports OpenSSL 1.1.1+, currently "
    #         f"the 'ssl' module is compiled with {ssl.OPENSSL_VERSION}. "
    #         "See: https://github.com/urllib3/urllib3/issues/2168"
    #     )
    # fmt: on
    pass
```
