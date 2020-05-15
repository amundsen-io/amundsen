import * as React from 'react';
import { shallow } from 'enzyme';

import { Footer, FooterProps, mapDispatchToProps, mapStateToProps } from '.';

import globalState from 'fixtures/globalState';

import * as DateUtils from 'utils/dateUtils';

const MOCK_DATE_STRING = 'Jan 1 2000 at 0:00:00 am';
jest.spyOn(DateUtils, 'formatDateTimeLong').mockReturnValue(MOCK_DATE_STRING);

describe('Footer', () => {
    let props: FooterProps;
    let subject;

    beforeEach(() => {
        props = {
          lastIndexed: 1555632106,
          getLastIndexed: jest.fn(),
        };
        subject = shallow(<Footer {...props} />);
    });

    describe('componentDidMount', () => {
        it('calls props.getLastIndexed', () => {
            expect(props.getLastIndexed).toHaveBeenCalled();
        });
    });

    describe('render', () => {
        it('calls generateDateTimeString if this.state.lastIndexed', () => {
            jest.spyOn(subject.instance(), 'generateDateTimeString');
            subject.instance().render();
            expect(subject.instance().generateDateTimeString).toHaveBeenCalled();
        });

        it('renders correct content if this.state.lastIndexed', () => {
            const expectedText = `Amundsen was last indexed on ${MOCK_DATE_STRING}`;
            expect(subject.find('#footer').props().children).toBeTruthy();
            expect(subject.find('#footer').text()).toEqual(expectedText);
        });

        it('renders no content if this.state.lastIndexed is null', () => {
            subject.setProps({ lastIndexed: null });
            expect(subject.find('#footer').props().children).toBeFalsy();
        });

        it('renders no content if this.state.lastIndexed is undefined', () => {
            subject.setProps({ lastIndexed: undefined });
            expect(subject.find('#footer').props().children).toBeFalsy();
        });
    });
});

describe('mapDispatchToProps', () => {
    let dispatch;
    let result;

    beforeEach(() => {
        dispatch = jest.fn(() => Promise.resolve());
        result = mapDispatchToProps(dispatch);
    });

    it('sets getLastIndexed on the props', () => {
        expect(result.getLastIndexed).toBeInstanceOf(Function);
    });
});

describe('mapStateToProps', () => {
    let result;
    beforeEach(() => {
        result = mapStateToProps(globalState);
    });

    it('sets lastIndexed on the props', () => {
        expect(result.lastIndexed).toEqual(globalState.tableMetadata.lastIndexed);
    });
});
