import * as React from 'react';
import { shallow } from 'enzyme';

import QueryList, { QueryListProps } from './';
import QueryListItem from '../QueryListItem';

import { ResourceType } from 'interfaces';

const setup = (propOverrides?: Partial<QueryListProps>) => {
  const props = {
    queries: [],
    ...propOverrides,
  };
  const wrapper = shallow<QueryList>(<QueryList {...props} />);

  return { props, wrapper };
};

describe('QueryList', () => {
  describe('render', () => {
    it('returns a list item for each query', () => {
      const { props, wrapper } = setup({
        queries: [
          {
            type: ResourceType.query,
            name: '2022-02-22 TEST QUERY NAME',
            query_text:
              "WITH\n\ncolumnName AS (\nSELECT  split_part(columnName, 'TEST', 2) as parameter,\n        SUM(amount) as vct_spend\nFROM    hive.core.fact_passenger_spends\nWHERE   ds >= '2020-02-26'\n    AND ds < '2020-03-04'\n    AND coupon_code like '%VCT%'\n    AND coupon_code like 'USAPAXENG%'\n    AND coupon_code NOT like '%PASS%' -- EXCLUDING RIDE PASSES DUE TO 5-WEEK SPEND\n    AND coupon_code NOT like '%10CAP1X75AD%'  -- NOT SURE WHY THIS COUPON WAS BEING DEPLOYED...\n    AND coupon_code NOT like '%QAR%' -- Q1 QAR test\nGROUP BY 1\n)\n\nSELECT  offer,\n        vct_spend\nFROM    offer_spends\nUNION\nSELECT  'TOTAL' as offer,\n        SUM(vct_spend) as vct_spend\nFROM    offer_spends\nUNION   \nSELECT  'AVG_SPEND' as offer,\n        SUM(vct_spend) / COUNT(offer) * 1.0 as vct_spend\nFROM    offer_spends\nORDER BY  1",
            url:
              'https://app.mode.com/company/reports/testID/queries/testQuery',
          },
          {
            type: ResourceType.query,
            name: '2022-02-23 TEST QUERY NAME TWO',
            query_text:
              "WITH\n\ncolumnName2 AS (\nSELECT  split_part(columnName2, 'TEST', 2) as parameter,\n        SUM(amount) as vct_spend\nFROM    hive.core.fact_passenger_spends\nWHERE   ds >= '2020-02-26'\n    AND ds < '2020-03-04'\n    AND coupon_code like '%VCT%'\n    AND coupon_code like 'USAPAXENG%'\n    AND coupon_code NOT like '%PASS%' -- EXCLUDING RIDE PASSES DUE TO 5-WEEK SPEND\n    AND coupon_code NOT like '%10CAP1X75AD%'  -- NOT SURE WHY THIS COUPON WAS BEING DEPLOYED...\n    AND coupon_code NOT like '%QAR%' -- Q1 QAR test\nGROUP BY 1\n)\n\nSELECT  offer,\n        vct_spend\nFROM    offer_spends\nUNION\nSELECT  'TOTAL' as offer,\n        SUM(vct_spend) as vct_spend\nFROM    offer_spends\nUNION   \nSELECT  'AVG_SPEND' as offer,\n        SUM(vct_spend) / COUNT(offer) * 1.0 as vct_spend\nFROM    offer_spends\nORDER BY  1",
            url:
              'https://app.mode.com/company/reports/testID2/queries/testQuery2',
          },
        ],
      });
      const expected = props.queries.length;
      const actual = wrapper.find(QueryListItem).length;

      expect(actual).toEqual(expected);
    });

    describe('when no queries available', () => {
      it('returns null', () => {
        const { wrapper } = setup();
        const expected = 0;
        const actual = wrapper.find(QueryListItem).length;

        expect(actual).toEqual(expected);
      });
    });
  });
});
