import axios from 'axios';

// TODO - Add better typing for response and error

export function announcementsGet() {
  return axios({
      method: 'get',
      url: '/api/announcements/v0/',
    })
    .then((response) => {
      return response.data.posts
    })
    .catch((error) => {
      console.log(error.response.data.msg);
      return error
    });
}
