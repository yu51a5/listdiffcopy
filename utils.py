

###############################################################################
def put_together_framed_message(message, char='*', max_chars=60):
  chars = char * min(max_chars, len(message) + 6)
  result = '\n'.join(['', chars, char * 2 + ' ' + message + ' ' + char * 2, chars, ''])
  return result

###############################################################################
def remove_char_and_after(s, c):
  i = s.find(c)
  return s[:i] if i > 0 else s
  
###############################################################################
def remove_duplicates(a_list, transform_func=None):
  if transform_func:
    dict_ = {transform_func(v) : v for v in a_list}
    result = [v for v in dict_.values()]
  else:
    result = [x for n, x in enumerate(a_list) if a_list.index(x) == n]
  return result

###############################################################################
def find_duplicates(a_list):
  result = [x for n, x in enumerate(a_list) if a_list.index(x) < n]
  return result


#################################################################################
def creates_multi_index(index_1, index_2):
  index_1_expanded = [i1  for i1 in index_1 for _ in index_2]
  index_2_expanded = index_2 * len(index_1)
  result = list(map(list, zip(index_1_expanded, index_2_expanded)))
  return result

#################################################################################
def partial_with_moving_back(func, func_for_args_to_move_back, kwargnames_to_move_back, /, *args, **keywords):
  def newfunc(*fargs, **fkeywords):
    keywords_to_move_back = {a : keywords.pop(a) for a in keywords if a in kwargnames_to_move_back}
    newkeywords = {**keywords, **fkeywords, **keywords_to_move_back}

    args_to_move_back = [a for a in args if func_for_args_to_move_back(a)]
    args0 = [a for a in args if not func_for_args_to_move_back(a)]

    return func(*args0, *fargs, *args_to_move_back, **newkeywords)

  return newfunc
  