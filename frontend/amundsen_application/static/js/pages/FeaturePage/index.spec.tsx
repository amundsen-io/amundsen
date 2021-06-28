// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0
import * as React from 'react';
import * as History from 'history';
import { shallow } from 'enzyme';

import globalState from 'fixtures/globalState';
import { featureCode, featureMetadata } from 'fixtures/metadata/feature';
import {
  FeaturePageLoader,
  FeaturePage,
  FeaturePageProps,
  mapDispatchToProps,
  mapStateToProps,
} from './index';

const setupLoader = () => {
  const wrapper = shallow(<FeaturePageLoader />);
  return wrapper;
};
describe('FeaturePageLoader', () => {
  it('should render without errors', () => {
    expect(() => {
      setupLoader();
    }).not.toThrow();
  });

  it('renders a mock header', () => {
    const wrapper = setupLoader();
    const expected = 1;
    const actual = wrapper.find('.resource-header').length;
    expect(actual).toEqual(expected);
  });

  it('renders three mock tabs', () => {
    const wrapper = setupLoader();
    const expected = 3;
    const actual = wrapper.find('.shimmer-tab').length;
    expect(actual).toEqual(expected);
  });
});

const setup = (
  propOverrides?: Partial<FeaturePageProps>,
  location?: Partial<History.Location>
) => {
  const props = {
    location,
    featureCode,
    isLoading: false,
    feature: featureMetadata,
    getFeatureDispatch: jest.fn(),
    getFeatureCodeDispatch: jest.fn(),
    ...propOverrides,
  };
  // @ts-ignore
  const wrapper = shallow<FeaturePage>(<FeaturePage {...props} />);
  return { props, wrapper };
};

describe('mapStateToProps', () => {
  it('returns expected props', () => {
    const result = mapStateToProps(globalState);
    const { feature } = globalState;
    expect(result.isLoading).toEqual(feature.isLoading);
    expect(result.statusCode).toEqual(feature.statusCode);
    expect(result.feature).toEqual(feature.feature);
    expect(result.featureCode).toEqual(feature.featureCode);
  });
});

describe('mapDispatchToProps', () => {
  let dispatch;
  let result;
  beforeAll(() => {
    dispatch = jest.fn(() => Promise.resolve());
    result = mapDispatchToProps(dispatch);
  });

  it('sets getFeatureDispatch props to trigger desired action', () => {
    expect(result.getFeatureDispatch).toBeInstanceOf(Function);
  });
  it('sets getFeatureCodeDispatch props to trigger desired action', () => {
    expect(result.getFeatureCodeDispatch).toBeInstanceOf(Function);
  });
});
