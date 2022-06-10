// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { shallow } from 'enzyme';

import { RequestMetadataType } from 'interfaces';
import { REQUEST_DESCRIPTION } from './constants';
import {
  RequestDescriptionText,
  mapDispatchToProps,
  RequestDescriptionTextProps,
} from '.';

describe('RequestDescriptionText', () => {
  const setup = (propOverrides?: Partial<RequestDescriptionTextProps>) => {
    const props: RequestDescriptionTextProps = {
      requestMetadataType: RequestMetadataType.TABLE_DESCRIPTION,
      openRequestDescriptionDialog: jest.fn(),
      ...propOverrides,
    };
    const wrapper = shallow<typeof RequestDescriptionText>(
      // eslint-disable-next-line react/jsx-props-no-spreading
      <RequestDescriptionText {...props} />
    );
    return { props, wrapper };
  };

  describe('openRequest', () => {
    it('calls openRequestDescriptionDialog for a table', () => {
      const { props, wrapper } = setup();
      const openRequestDescriptionDialogSpy = jest.spyOn(
        props,
        'openRequestDescriptionDialog'
      );
      wrapper.find('.request-description').simulate('click');
      expect(openRequestDescriptionDialogSpy).toHaveBeenCalledWith(
        RequestMetadataType.TABLE_DESCRIPTION,
        undefined
      );
    });

    it('calls openRequestDescriptionDialog for a column', () => {
      const columnName = 'column';
      const { props, wrapper } = setup({
        requestMetadataType: RequestMetadataType.COLUMN_DESCRIPTION,
        columnName,
      });
      const openRequestDescriptionDialogSpy = jest.spyOn(
        props,
        'openRequestDescriptionDialog'
      );
      wrapper.find('.request-description').simulate('click');
      expect(openRequestDescriptionDialogSpy).toHaveBeenCalledWith(
        RequestMetadataType.COLUMN_DESCRIPTION,
        columnName
      );
    });
  });

  describe('render', () => {
    it('renders Request Description button with correct text', () => {
      const { wrapper } = setup();
      expect(wrapper.find('.request-description').text()).toEqual(
        REQUEST_DESCRIPTION
      );
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
