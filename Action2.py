from ActionBase import ActionBase

#################################################################################
class Action2(ActionBase):

  #################################################################################
  def __init__(self, path_from, path_to, storage_from=None, storage_to=None, StorageFromType=None, StorageToType=None, kwargs_from={}, kwargs_to={}, **kwargs):
    self.root_path_from = path_from
    self.root_path_to = path_to

    #self.index_comp_df = pd.MultiIndex.from_tuples(creates_multi_index(self.index_listing_df, self.status_names))

    errors = ActionBase._check_storage_or_type(storage=storage_from, StorageType=StorageFromType, kwargs=kwargs_from) \
           + ActionBase._check_storage_or_type(storage=storage_to  , StorageType=StorageToType  , kwargs=kwargs_to)

    assert not errors, '.\n'.join(['ERRORS:'] + errors)

    self.storage_from = storage_from if storage_from else None
    self.storage_to   = storage_to   if storage_to   else None

    if self.storage_from and not self.storage_to and StorageToType == type(self.storage_from) and self.storage_from.check_if_constructor_kwargs_are_the_same(kwargs_to):
      self.storage_to = self.storage_from
    if self.storage_to and not self.storage_from and StorageFromType == type(self.storage_to) and self.storage_to.check_if_constructor_kwargs_are_the_same(kwargs_from):
      self.storage_from = self.storage_to

    if self.storage_to and self.storage_from:
      self.__common_part_of_constructor(**kwargs)
    elif self.storage_to and (not self.storage_from):
      with StorageFromType(**kwargs_from) as self.storage_from:
        self.__common_part_of_constructor(**kwargs)
    elif self.storage_from and (not self.storage_to):
      with StorageToType(**kwargs_to) as self.storage_to:
        self.__common_part_of_constructor(**kwargs)
    else:
      with StorageFromType(**kwargs_from) as self.storage_from:
        if StorageFromType == StorageToType and kwargs_from == kwargs_to:
          self.storage_to = self.storage_from
          self.__common_part_of_constructor(**kwargs)
        else:
          with StorageToType(**kwargs_to) as self.storage_to: 
            self.__common_part_of_constructor(**kwargs)

  #################################################################################
  def __common_part_of_constructor(self, **kwargs):
    title = self._put_title_together()
    super().__init__(title=title)
    self._common_part_of_constructor(**kwargs)

  #################################################################################
  def _common_part_of_constructor(self, **kwargs):
    raise Exception("needs to be overriden", type(self))

  #################################################################################
  def _put_title_together(self):
    raise Exception("needs to be overriden", type(self))
    