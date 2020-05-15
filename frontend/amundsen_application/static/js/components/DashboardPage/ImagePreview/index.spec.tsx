import * as React from 'react';

import { shallow } from 'enzyme';

import Linkify from 'react-linkify'

import { ImagePreview, ImagePreviewProps } from './';

import ShimmeringDashboardLoader from '../ShimmeringDashboardLoader';

import * as Constants from './constants';

describe('ImagePreview', () => {
  const setup = (propOverrides?: Partial<ImagePreviewProps>) => {
    const props = {
      uri: 'test:uri/value',
      redirectUrl: 'someUrl',
      ...propOverrides,
    };

    const wrapper = shallow<ImagePreview>(<ImagePreview {...props} />)
    return { props, wrapper };
  };

  describe('onSuccess', () => {
    let currentState;
    beforeAll(() => {
      const { props, wrapper } = setup();
      wrapper.instance().onSuccess();
      currentState = wrapper.state();
    });
    it('sets the loading state to false', () => {
      expect(currentState.isLoading).toBe(false);
    });
    it('sets the hasError state to false', () => {
      expect(currentState.hasError).toBe(false);
    })
  });

  describe('onError', () => {
    let currentState;
    beforeAll(() => {
      const { props, wrapper } = setup();
      const event = {} as React.SyntheticEvent<HTMLImageElement>;
      wrapper.instance().onError(event);
      currentState = wrapper.state();
    });
    it('sets the loading state to false', () => {
      expect(currentState.isLoading).toBe(false);
    });
    it('sets the hasError state to false', () => {
      expect(currentState.hasError).toBe(true);
    })
  });

  describe('render', () => {
    describe('if no error', () => {
      describe('when loading', () => {
        let wrapper;
        beforeAll(() => {
          wrapper = setup().wrapper;
          wrapper.instance().setState({ isLoading: true, hasError: false });
        });

        it('renders the loading dashboard', () => {
          expect(wrapper.find(ShimmeringDashboardLoader).exists()).toBeTruthy();
        });

        it('renders hidden img', () => {
          expect(wrapper.find('img').props().style).toEqual({ visibility: 'hidden' });
        });
      });

      describe('when not loading', () => {
        let props;
        let wrapper;
        beforeAll(() => {
          const setupResult = setup();
          props = setupResult.props
          wrapper = setupResult.wrapper;
          wrapper.instance().setState({ isLoading: false, hasError:false });
        });
        it('renders visible img with correct props', () => {
          const elementProps = wrapper.find('img').props();
          expect(elementProps.style).toEqual({ visibility: 'visible' });
          expect(elementProps.src).toEqual(`${Constants.PREVIEW_BASE}/${props.uri}/${Constants.PREVIEW_END}`);
          expect(elementProps.onLoad).toBe(wrapper.instance().onSuccess);
          expect(elementProps.onError).toBe(wrapper.instance().onError);
        });
      })
    });

    it('renders link if hasError', () => {
      const { props, wrapper } = setup();
      wrapper.instance().setState({ hasError: true });
      expect(wrapper.find(Linkify).exists()).toBeTruthy();
    });
  });
});
