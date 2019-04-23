import * as React from 'react';

import { shallow } from 'enzyme';

import { Overlay, Popover, Tooltip } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import EditableText, { EditableTextProps } from '../';

describe('EditableText', () => {
    let props: EditableTextProps;
    let subject;

    beforeEach(() => {
        props = {
          editable: true,
          maxLength: 250,
          onSubmitValue: jest.fn(),
          getLatestValue: jest.fn(),
          refreshValue: 'newValue',
          value: 'currentValue',
        };
        subject = shallow(<EditableText {...props} />);
    });

    describe('render', () => {
        it('renders value in a div if not editable', () => {
            props.editable = false;
             /* Note: Do not copy this pattern, for some reason setProps is not updating the content in this case */
            subject = shallow(<EditableText {...props} />);
            expect(subject.find('div#editable-text').text()).toEqual(props.value);
        });

        describe('renders correctly if !this.state.inEditMode', () => {
            beforeEach(() => {
                subject.setState({ inEditMode: false });
            });
            it('renders value as first child', () => {
                expect(subject.find('#editable-text').props().children[0]).toEqual(props.value);
            });

            it('renders edit link to enterEditMode', () => {
                expect(subject.find('#editable-text').find('a').props().onClick).toEqual(subject.instance().enterEditMode);
            });

            it('renders edit link with correct class if state.value exists', () => {
                expect(subject.find('#editable-text').find('a').props().className).toEqual('edit-link');
            });

            it('renders edit link with correct text if state.value exists', () => {
                expect(subject.find('#editable-text').find('a').text()).toEqual('edit');
            });

            it('renders edit link with correct class if state.value does not exist', () => {
                subject.setState({ value: null });
                expect(subject.find('#editable-text').find('a').props().className).toEqual('edit-link no-value');
            });

            it('renders edit link with correct text if state.value does not exist', () => {
                subject.setState({ value: null });
                expect(subject.find('#editable-text').find('a').text()).toEqual('Add Description');
            });
        });

        /* TODO: The use of ReactDOM.findDOMNode is difficult to test, preventing further coverage
        describe('renders correctly if this.state.inEditMode && this.state.isDisabled', () => {
            beforeEach(() => {
                subject.setState({ inEditMode: true, isDisabled: true });
            });
            it('renders value as first child', () => {
                expect(subject.find('#editable-text').props().children[0]).toEqual(props.value);
            });

            it('renders edit link to enterEditMode', () => {
                expect(subject.find('#editable-text').find('a').props().onClick).toEqual(subject.instance().enterEditMode);
            });

            it('renders edit link with correct class if state.value exists', () => {
                expect(subject.find('#editable-text').find('a').props().className).toEqual('edit-link');
            });

            it('renders edit link with correct text if state.value exists', () => {
                expect(subject.find('#editable-text').find('a').text()).toEqual('edit');
            });

            it('renders edit link with correct class if state.value does not exist', () => {
                subject.setState({ value: null });
                expect(subject.find('#editable-text').find('a').props().className).toEqual('edit-link no-value');
            });

            it('renders edit link with correct text if state.value does not exist', () => {
                subject.setState({ value: null });
                expect(subject.find('#editable-text').find('a').text()).toEqual('Add Description');
            });

            // TODO: Test Overlay & Tooltip
        });
        */

        // TODO: Test rendering of textarea with Overlay & Tooltip
    });

    // TODO: Test component methods
});
