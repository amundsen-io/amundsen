import axios from 'axios';

function transformSearchResults(data) {
  return {
    pageIndex: data.page_index,
    searchResults: data.results,
    searchTerm: data.search_term,
    totalResults: data.total_results,
  };
}

export function searchExecuteSearch(action) {
  const { term, pageIndex } = action;
  return axios.get(`/api/search?query=${term}&page_index=${pageIndex}`)
  .then(response => transformSearchResults(response.data))
  .catch(() => transformSearchResults(error.response.data));
}
