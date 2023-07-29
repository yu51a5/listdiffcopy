dry_run = False

def do_dry_run():
  global dry_run
  dry_run = True

def is_dry_run():
  global dry_run
  return dry_run