import axios, { AxiosResponse } from 'axios';
import { Issue } from 'interfaces';

export const API_PATH = '/api/issue';

export type IssuesAPI = {
  issues: {
    issues: Issue[]; 
    remaining: number;  
    remaining_url: string; 
  }
}

export type IssueApi = {
  issue: Issue; 
}

export function getIssues(tableKey: string) {
  return axios.get(`${API_PATH}/issues?key=${tableKey}`)
  .then((response: AxiosResponse<IssuesAPI>) => {
    return response.data.issues;
  });
}

export function createIssue(data: FormData) {
  const headers =  {'Content-Type': 'multipart/form-data' };
  return axios.post(`${API_PATH}/issue`, data, { headers }
    ).then((response: AxiosResponse<IssueApi>) => {
      return response.data.issue; 
    });
}

