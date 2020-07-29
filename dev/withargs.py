# https://github.com/streamlit/streamlit/issues/337

import os
import sys
import random
import argparse
import streamlit as st

parser = argparse.ArgumentParser(description='This app lists animals')

parser.add_argument('--animal', action='append', default=[],
                    help="Add one or more animals of your choice")
sort_order_choices = ('up', 'down', 'random')
parser.add_argument('--sort', choices=sort_order_choices, default='up',
                    help='Animal sort order (default: %(default)s)')
parser.add_argument('--uppercase', action='store_true',
                    help='Make the animals bigger!')
try:
    args = parser.parse_args()
except SystemExit as e:
    # This exception will be raised if --help or invalid command line arguments
    # are used. Currently streamlit prevents the program from exiting normally
    # so we have to do a hard exit.
    os._exit(e.code)

st.title("Command line example app")
st.markdown(f"Your current command line is: {sys.argv}")
