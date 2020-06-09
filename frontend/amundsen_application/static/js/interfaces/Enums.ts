export enum UpdateMethod {
  PUT = 'PUT',
  DELETE = 'DELETE',
}

export enum FilterType {
  CHECKBOX_SELECT = 'checkboxFilter',
  INPUT_SELECT = 'inputFilter',
}

export enum SearchType {
  CLEAR_TERM = 'clear_search_term',
  FILTER = 'update_filter',
  INLINE_SEARCH = 'inline_search',
  INLINE_SELECT = 'inline_select',
  LOAD_URL = 'load_url',
  PAGINATION = 'update_page',
  SUBMIT_TERM = 'submit_search_term',
}
