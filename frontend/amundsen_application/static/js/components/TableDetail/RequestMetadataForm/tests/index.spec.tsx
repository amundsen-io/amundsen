import * as React from 'react';
import { shallow } from 'enzyme';

import FlashMessage from 'components/common/FlashMessage';

import globalState from 'fixtures/globalState';
import { NotificationType, SendingState } from 'interfaces';
import { RequestMetadataForm, mapDispatchToProps, mapStateToProps, RequestMetadataProps } from '../';
import {
  TITLE_TEXT,
  FROM_LABEL,
  TO_LABEL,
  REQUEST_TYPE,
  TABLE_DESCRIPTION,
  COLUMN_DESCRIPTIONS,
  ADDITIONAL_DETAILS,
  SEND_BUTTON,
  SEND_FAILURE_MESSAGE,
  SEND_INPROGRESS_MESSAGE,
  SEND_SUCCESS_MESSAGE,
} from '../constants'

const mockFormData = {
  'recipients': 'test1@test.com,test2@test.com',
  'sender': 'test@test.com',
  'table-description': 'on',
  'fields-requested': 'off',
  'comment': 'test',
  get: jest.fn(),
}
mockFormData.get.mockImplementation((val) => {
  return mockFormData[val];
})
// @ts-ignore: How to mock FormData without TypeScript error?
global.FormData = () => (mockFormData);

describe('RequestMetadataForm', () => {
  const setup = (propOverrides?: Partial<RequestMetadataProps>) => {
    const props: RequestMetadataProps = {
      userEmail: 'test0@lyft.com',
      displayName: '',
      tableOwners: ['test1@lyft.com', 'test2@lyft.com'],
      submitNotification: jest.fn(),
      requestIsOpen: true,
      sendState: SendingState.IDLE,
      closeRequestDescriptionDialog: jest.fn(),
      ...propOverrides,
    };
    const wrapper = shallow<RequestMetadataForm>(<RequestMetadataForm {...props} />);
    return {props, wrapper}
  };

  describe('componentWillUnmount', () => {
    it('calls closeRequestDescriptionDialog', () => {
      const { props, wrapper } = setup();
      const closeRequestDescriptionDialogSpy = jest.spyOn(props, 'closeRequestDescriptionDialog');
      wrapper.instance().componentWillUnmount();
      expect(closeRequestDescriptionDialogSpy).toHaveBeenCalled();
    });
  });

  describe('closeDialog', () => {
    it('calls closeRequestDescriptionDialog', () => {
      const { props, wrapper } = setup();
      const closeRequestDescriptionDialogSpy = jest.spyOn(props, 'closeRequestDescriptionDialog');
      wrapper.instance().closeDialog();
      expect(closeRequestDescriptionDialogSpy).toHaveBeenCalled();
    });
  });

  describe('getFlashMessageString', () => {
    it('returns SEND_SUCCESS_MESSAGE if SendingState.COMPLETE', () => {
      const wrapper = setup({ sendState: SendingState.COMPLETE }).wrapper;
      expect(wrapper.instance().getFlashMessageString()).toEqual(SEND_SUCCESS_MESSAGE);
    });
    it('returns SEND_FAILURE_MESSAGE if SendingState.ERROR', () => {
      const wrapper = setup({ sendState: SendingState.ERROR }).wrapper;
      expect(wrapper.instance().getFlashMessageString()).toEqual(SEND_FAILURE_MESSAGE);
    });
    it('returns SEND_INPROGRESS_MESSAGE if SendingState.WAITING', () => {
      const wrapper = setup({ sendState: SendingState.WAITING }).wrapper;
      expect(wrapper.instance().getFlashMessageString()).toEqual(SEND_INPROGRESS_MESSAGE);
    });
    it('returns empty striong if sending state not handled', () => {
      const wrapper = setup({ sendState: SendingState.IDLE }).wrapper;
      expect(wrapper.instance().getFlashMessageString()).toEqual('');
    });
  });

  describe('renderFlashMessage', () => {
    let wrapper;
    let mockString;
    let getFlashMessageStringMock;
    beforeAll(() => {
      wrapper = setup().wrapper;
      mockString = 'I am the message'
      getFlashMessageStringMock = jest.spyOn(wrapper.instance(), 'getFlashMessageString').mockImplementation(() => {
        return mockString;
      });
    });

    it('renders a FlashMessage with correct props', () => {
      const element = wrapper.instance().renderFlashMessage();
      expect(element.props.iconClass).toEqual('icon-mail');
      expect(element.props.message).toBe(mockString);
      expect(element.props.onClose).toEqual(wrapper.instance().closeDialog);
    });
  });

  describe('submitNotification', () => {
    it('calls submitNotification', () => {
      const { props, wrapper } = setup();
      const submitNotificationSpy = jest.spyOn(props, 'submitNotification');
      wrapper.instance().submitNotification({ preventDefault: jest.fn() });
      expect(submitNotificationSpy).toHaveBeenCalledWith(
        mockFormData['recipients'].split(','),
        mockFormData['sender'],
        NotificationType.METADATA_REQUESTED,
        {
          comment: mockFormData['comment'],
          resource_name: props.displayName,
          resource_url: window.location.href,
          description_requested: true,
          fields_requested: false,
        }
      );
    });
  });

  describe('render', () => {
    let props;
    let wrapper;
    let element;

    describe('when this.props.requestIsOpen', () => {
      beforeAll(() => {
        const setupResult = setup();
        props = setupResult.props;
        wrapper = setupResult.wrapper;
      });
      it('renders header title', () => {
        element = wrapper.find('#request-metadata-title');
        expect(element.find('h3').text()).toEqual(TITLE_TEXT);
      });
      it('renders close button', () => {
        element = wrapper.find('#request-metadata-title');
        expect(element.find('button').exists()).toEqual(true);
      });

      it('renders from input with current user', () => {
        element = wrapper.find('#sender-form-group');
        expect(element.find('input').props().value).toEqual('test0@lyft.com');
      });

      it('renders from label', () => {
        element = wrapper.find('#sender-form-group');
        expect(element.find('label').text()).toEqual(FROM_LABEL);
      });
      it('renders from input with current user', () => {
        element = wrapper.find('#sender-form-group');
        expect(element.find('input').props().value).toEqual('test0@lyft.com');
      });

      it('renders to label', () => {
        element = wrapper.find('#recipients-form-group');
        expect(element.find('label').text()).toEqual(TO_LABEL);
      });
      it('renders to input with correct recipients', () => {
        element = wrapper.find('#recipients-form-group');
        expect(element.find('input').props().defaultValue).toEqual('test1@lyft.com,test2@lyft.com');
      });

      it('renders request type label', () => {
        element = wrapper.find('#request-type-form-group');
        expect(element.find('label').at(0).text()).toEqual(REQUEST_TYPE);
      });
      it('renders table description checkbox', () => {
        element = wrapper.find('#request-type-form-group');
        expect(element.find('label').at(1).text()).toEqual(TABLE_DESCRIPTION);
      });
      it('renders column descriptions checkbox', () => {
        element = wrapper.find('#request-type-form-group');
        expect(element.find('label').at(2).text()).toEqual(COLUMN_DESCRIPTIONS);
      });

      it('renders additional details label', () => {
        element = wrapper.find('#additional-comments-form-group');
        expect(element.find('label').text()).toEqual(ADDITIONAL_DETAILS);
      });
      it('renders empty textarea', () => {
        element = wrapper.find('#additional-comments-form-group');
        expect(element.find('textarea').text()).toEqual('');
      });

      it('renders submit button with correct text', () => {
        element = wrapper.find('#submit-request-button');
        expect(element.text()).toEqual(SEND_BUTTON);
      });
    });

    describe('when !this.props.requestIsOpen', () => {
      beforeAll(() => {
        const setupResult = setup({ requestIsOpen: false });
        props = setupResult.props;
        wrapper = setupResult.wrapper;
      });

      it('renders nothing', () => {
        expect(wrapper).toEqual({});
      });
    });

    describe('when sendState is not SendingState.IDLE', () => {
      let wrapper;
      let renderFlashMessageMock;
      beforeAll(() => {
        wrapper = setup({ sendState: SendingState.WAITING, requestIsOpen: false }).wrapper;
        renderFlashMessageMock = jest.spyOn(wrapper.instance(), 'renderFlashMessage');
      });

      it('renders results of renderFlashMessage() within component', () => {
        wrapper.instance().render();
        expect(wrapper.props().className).toEqual('request-component');
        expect(renderFlashMessageMock).toHaveBeenCalledTimes(1);
      });
    });
  });

  describe('mapStateToProps', () => {
    let result;
    beforeAll(() => {
      result = mapStateToProps(globalState);
    });

    it('sets userEmail on the props', () => {
      expect(result.userEmail).toEqual(globalState.user.loggedInUser.email);
    });
    it('sets displayName on the props', () => {
      expect(result.displayName).toEqual(globalState.tableMetadata.tableData.schema + '.' + globalState.tableMetadata.tableData.table_name);
    });
    it('sets ownerObj on the props', () => {
      expect(result.tableOwners).toEqual(Object.keys(globalState.tableMetadata.tableOwners.owners));
    });
    it('sets requestIsOpen on the props', () => {
      expect(result.requestIsOpen).toEqual(globalState.notification.requestIsOpen);
    });
    it('sets sendState on the props', () => {
      expect(result.sendState).toEqual(globalState.notification.sendState);
    });
  });

  describe('mapDispatchToProps', () => {
    let dispatch;
    let result;
    beforeAll(() => {
      dispatch = jest.fn(() => Promise.resolve());
      result = mapDispatchToProps(dispatch);
    });

    it('sets submitNotification on the props', () => {
      expect(result.submitNotification).toBeInstanceOf(Function);
    });

    it('sets closeRequestDescriptionDialog on the props', () => {
      expect(result.closeRequestDescriptionDialog).toBeInstanceOf(Function);
    });
  });
});
