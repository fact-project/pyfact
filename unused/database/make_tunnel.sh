#!/bin/bash
ssh -f -L 37017:localhost:27017 fact@ihp-pc41.ethz.ch -N

# test if it worked e.g. by typing:
# mongo --port 37017 aux
