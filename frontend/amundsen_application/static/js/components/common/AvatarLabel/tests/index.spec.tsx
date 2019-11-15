import * as React from 'react';
import * as Avatar from 'react-avatar';

import { shallow } from 'enzyme';

import AvatarLabel, { AvatarLabelProps } from '../';

describe('AvatarLabel', () => {
  const setup = (propOverrides?: Partial<AvatarLabelProps>) => {
    const props: AvatarLabelProps = {
      ...propOverrides
    };
    const wrapper = shallow(<AvatarLabel {...props} />);
    return { props, wrapper };
  };

  describe('render', () => {
    let props: AvatarLabelProps;
    let wrapper;
    beforeAll(() => {
      const setupResult = setup({
        label: 'testLabel',
        src: 'testSrc',
      });
      props = setupResult.props;
      wrapper = setupResult.wrapper;
    });
    it('renders Avatar with correct props', () => {
      expect(wrapper.find(Avatar).props()).toMatchObject({
        name: props.label,
        src: props.src,
        size: 24,
        round: true,
      });
    });

    it('renders label with correct text', () => {
      expect(wrapper.find('.avatar-label').text()).toEqual(props.label);
    });
  });
});
