#!/bin/bash

# https://stackoverflow.com/a/246128
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
ROOT_DIR=$(realpath $SCRIPT_DIR/..)

mkdir -p $ROOT_DIR/secrets
openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out $ROOT_DIR/secrets/jwt.pem
