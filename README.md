# locale

## steps for ganache

start ganache with the utility `ganache`

```
$ ./ganache
```
## steps for IPFS

These are the steps for sending data to IPFS. Note that the instructions from
the [main
site](https://docs.ipfs.tech/quickstart/publish_cli/#install-and-register-to-w3)
are wrong. lack of `register` step. Se below the correct execution.

```
$ npm install -g @web3-storage/w3cli
$ w3 authorize <your@email.com>
$ w3 space create Pictures
$ w3 space register --email <your@email.com>
$ w3 up welcome-to-IPFS.jpg
```
