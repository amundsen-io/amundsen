import * as React from 'react';

import { shallow } from 'enzyme';

import { RequestDescriptionText, mapDispatchToProps, RequestDescriptionTextProps } from '.';
import globalState from 'fixtures/globalState';
import { REQUEST_DESCRIPTION } from './constants';
import { RequestMetadataType } from 'interfaces';

describe('RequestDescriptionText', () => {
  const setup = (propOverrides?: Partial<RequestDescriptionTextProps>) => {
    const props: RequestDescriptionTextProps = {
      openRequestDescriptionDialog: jest.fn(),
      ...propOverrides,
    };
    const wrapper = shallow<RequestDescriptionText>(<RequestDescriptionText {...props} />)
    return {props, wrapper}
  };

  describe('openRequest', () => {
    it('calls openRequestDescriptionDialog', () => {
      const { props, wrapper } = setup();
      const openRequestDescriptionDialogSpy = jest.spyOn(props, 'openRequestDescriptionDialog');
      wrapper.instance().openRequest();
      expect(openRequestDescriptionDialogSpy).toHaveBeenCalledWith(RequestMetadataType.TABLE_DESCRIPTION);
    });
  });

  describe('render', () => {
    it('renders Request Description button with correct text', () => {
      const { props, wrapper } = setup();
      wrapper.instance().render();
      expect(wrapper.find('.request-description').text()).toEqual(REQUEST_DESCRIPTION);
    });
  });

  describe('mapDispatchToProps', () => {
    let dispatch;
    let result;
    beforeAll(() => {
      dispatch = jest.fn(() => Promise.resolve());
      result = mapDispatchToProps(dispatch);
    });

    it('sets openRequestDescriptionDialog on the props', () => {
      expect(result.openRequestDescriptionDialog).toBeInstanceOf(Function);
    });
  });
});
