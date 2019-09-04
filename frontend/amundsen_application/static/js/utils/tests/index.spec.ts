import * as NavigationUtils from 'utils/navigation-utils';
import * as qs from 'simple-query-string';
import { ResourceType } from 'interfaces/Resources';


describe('Navigation utils', () => {
  describe('updateSearchUrl', () => {

    let historyReplaceSpy;
    let historyPushSpy;
    let searchParams;
    let expectedQueryString;
    beforeAll(() => {
      historyReplaceSpy = jest.spyOn(NavigationUtils.BrowserHistory, 'replace');
      historyPushSpy = jest.spyOn(NavigationUtils.BrowserHistory, 'push');

      searchParams = {
        term: 'test',
        resource: ResourceType.table,
        index: 0,
      };
      expectedQueryString = `/search?${qs.stringify(searchParams)}`;
    });

    it('calls history.replace when replace is true', () => {
      historyReplaceSpy.mockClear();
      historyPushSpy.mockClear();

      const replace = true;
      NavigationUtils.updateSearchUrl(searchParams, replace);

      expect(historyReplaceSpy).toHaveBeenCalledWith(expectedQueryString);
      expect(historyPushSpy).not.toHaveBeenCalled();
    });


    it('calls history.push when replace is false', () => {
      historyReplaceSpy.mockClear();
      historyPushSpy.mockClear();

      const replace = false;
      NavigationUtils.updateSearchUrl(searchParams, replace);

      expect(historyReplaceSpy).not.toHaveBeenCalled();
      expect(historyPushSpy).toHaveBeenCalledWith(expectedQueryString);
    });
  });
});
