import * as React from 'react';

import { shallow } from 'enzyme';

import { Link } from 'react-router-dom';
import Breadcrumb, { BreadcrumbProps } from '../';

describe('Breadcrumb', () => {
    let props: BreadcrumbProps;
    let subject;

    beforeEach(() => {
        props = {
          path: 'testPath',
          text: 'testText',
        };
        subject = shallow(<Breadcrumb {...props} />);
    });

    describe('render', () => {
        it('renders Link with correct path', () => {
            expect(subject.find(Link).props()).toMatchObject({
                to: props.path,
            });
        });

        it('renders button with correct text within the Link', () => {
            expect(subject.find(Link).find('button').text()).toEqual(props.text);
        });
    });
});
