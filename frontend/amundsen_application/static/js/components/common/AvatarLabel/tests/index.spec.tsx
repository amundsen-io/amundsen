import * as React from 'react';

import { mount, shallow } from 'enzyme';

import { Avatar } from 'react-avatar';
import AvatarLabel, { AvatarLabelProps } from '../';

describe('AvatarLabel', () => {
    let props: AvatarLabelProps;
    let subject;

    beforeEach(() => {
        props = {
          label: 'testLabel',
          src: 'testSrc',
        };
        subject = shallow(<AvatarLabel {...props} />);
    });

    describe('render', () => {
        it('renders Avatar with correct props', () => {
            /* Note: subject.find(Avatar) does not work - workaround is to directly check the content */
            const expectedContent = <Avatar name={props.label} src={props.src} size={24} round={true} />;
            expect(subject.find('#component-avatar').props().children).toEqual(expectedContent);
        });

        it('renders label with correct text', () => {
            expect(subject.find('#component-label').text()).toEqual(props.label);
        });
    });
});
