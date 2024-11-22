import json
import matplotlib.pyplot as plt
import sys
import numpy as np

success='Success'
general_failure='General failure to replay'
unknownSMTType='unknown SMT type'
unknownSMTTerm='unknown SMT term'
unknownSMTParsing='unknown error parsing SMT-LIB term/typ'
errorAST='Error parsing SMTLIB into the AST SMTLIB tree'
replay_error='Failure to replay specific rule'
timeout='Reconstruction Timeout'
noProof='Solver did not produce proof'

error_mapping = {
    0: success,
    1: general_failure,
    2: unknownSMTType,
    3: unknownSMTTerm,
    4: unknownSMTParsing,
    5: errorAST,
    6: replay_error,
    7: timeout,
    8: noProof
}

colors = {
  0: "#87bc45",
  1: "#f46a9b",
  2: "#ea5545",
  3: "#ef9b20",
  4: "#edbf33",
  5: "#ede15b",
  6: "red",
  7: "#b33dc6",
  8: "#27aeef"
}    

def error_codes_to_str(error_code):
  return error_mapping.get(abs(error_code), "Invalid Error Code")

def print_error_dict(err_dict):
  for key in err_dict:
    if key <= 8 :
      print(error_mapping[key]+ ': '+str(err_dict[key]))

def get_colors():
  return colors
