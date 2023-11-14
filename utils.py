

###############################################################################
def put_together_framed_message(message, char='*'):
  chars = char * (len(message) + 6)
  result = '\n'.join(['', chars, char * 2 + ' ' + message + ' ' + char * 2, chars, ''])
  return result

###############################################################################
def remove_duplicates(a_list):
  result = [x for n, x in enumerate(a_list) if a_list.index(x) == n]
  return result

def find_duplicates(a_list):
  result = [x for n, x in enumerate(a_list) if a_list.index(x) < n]
  return result
