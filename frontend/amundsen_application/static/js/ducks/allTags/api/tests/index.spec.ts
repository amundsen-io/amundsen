import axios, { AxiosResponse } from 'axios';

import { Tag } from 'interfaces';

import { metadataAllTags, AllTagsResponseAPI } from '../v0';

describe('metadataAllTags', () => {
  it('resolves with array of sorted result of response.data.tags on success', async () => {
    const rawTags: Tag[] = [
      {tag_count: 2, tag_name: 'test'},
      {tag_count: 1, tag_name: 'atest'}
    ];
    const expectedTags: Tag[] = [
      {tag_count: 1, tag_name: 'atest'},
      {tag_count: 2, tag_name: 'test'}
    ];
    const mockResponse: AxiosResponse<AllTagsResponseAPI> = {
      data: {
        tags: rawTags,
        msg: 'Success'
      },
      status: 200,
      statusText: '',
      headers: {},
      config: {}
    };

    const axiosMock = jest.spyOn(axios, 'get').mockImplementation(() => Promise.resolve(mockResponse));
    expect.assertions(1);
    await metadataAllTags().then(sortedTags => {
      expect(sortedTags).toEqual(expectedTags);
    });
  });
});
