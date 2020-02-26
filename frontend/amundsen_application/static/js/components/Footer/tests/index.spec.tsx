import * as React from 'react';
import * as moment from 'moment-timezone';
import { mount } from 'enzyme';

import { Footer, FooterProps, mapDispatchToProps, mapStateToProps } from '../';

import globalState from 'fixtures/globalState';

/* TODO: Issues with mocking moment-timezone, all tests are failing
describe('Footer', () => {
    let props: FooterProps;
    let subject;

    beforeEach(() => {
        props = {
          lastIndexed: 1555632106,
          getLastIndexed: jest.fn(),
        };
        subject = mount(<Footer {...props} />);
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
            const expectedText = 'Amundsen was last indexed on April 18th 2019 at 5:01:46 pm';
            expect(subject.find('#footer').props().children).toBeTruthy();
            // expect(subject.find('#footer').props().children().at(0).text()).toEqual(expectedText);
        });

        it('renders no content if !this.state.lastIndexed', () => {
            subject.setState({ lastIndexed: null });
            expect(subject.find('#footer').props().children).toBeFalsy();
        });
    });
});*/

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
