import * as React from 'react';
import { shallow } from 'enzyme';

import {
  mapDispatchToProps,
  mapStateToProps,
  ResourceSelector,
  ResourceSelectorProps } from '../';
import { TABLE_RESOURCE_TITLE, USER_RESOURCE_TITLE } from 'components/SearchPage/constants';

import AppConfig from 'config/config';
import globalState from 'fixtures/globalState';
import { ResourceType } from 'interfaces/Resources';


describe('ResourceSelector', () => {
  const setup = (propOverrides?: Partial<ResourceSelectorProps>) => {
    const props = {
      resource: ResourceType.table,
      tables: globalState.search.tables,
      users: globalState.search.users,
      dashboards: globalState.search.dashboards,
      setResource: jest.fn(),
      ...propOverrides
    };
    const wrapper = shallow<ResourceSelector>(<ResourceSelector {...props} />);
    return { props, wrapper };
  };

  describe('renderRadioOption', () => {
    const { wrapper, props } = setup();
    const instance = wrapper.instance();
    const radioConfig = {
      type: ResourceType.table,
      label: TABLE_RESOURCE_TITLE,
      count: 10,
    };
    const content = shallow(instance.renderRadioOption(radioConfig, 0));

    it('renders an input with correct properties', () => {
      const inputProps = content.find('input').props();
      expect(inputProps.type).toEqual("radio");
      expect(inputProps.name).toEqual("resource");
      expect(inputProps.value).toEqual(radioConfig.type);
      expect(inputProps.checked).toEqual(props.resource === radioConfig.type);
      expect(inputProps.onChange).toEqual(instance.onChange);
    });

    it('renders with the correct labels', () => {
      expect(content.text()).toEqual(`${radioConfig.label}${radioConfig.count}`)
    });
  });
  
  describe('onChange', () => {
    it('calls setResource with the appropriate resource type', () => {
      const mockEvent = {
        target: {
          value: ResourceType.table,
        }
      };
      const { wrapper, props } = setup();
      const setResourceSpy = jest.spyOn(props, "setResource")
      wrapper.instance().onChange(mockEvent);
      expect(setResourceSpy).toHaveBeenCalledWith(mockEvent.target.value)
    });
  });

  describe('render', () => {
    let props;
    let wrapper;

    let tableOptionConfig;
    let userOptionConfig;
    let renderRadioOptionSpy;

    beforeAll(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;

      tableOptionConfig = {
        type: ResourceType.table,
        label: TABLE_RESOURCE_TITLE,
        count: props.tables.total_results,
      };
      userOptionConfig = {
        type: ResourceType.user,
        label: USER_RESOURCE_TITLE,
        count: props.users.total_results,
      };

      renderRadioOptionSpy = jest.spyOn(wrapper.instance(), 'renderRadioOption');
    });

    it('renders the table resource option', () => {
      renderRadioOptionSpy.mockClear();
      wrapper.instance().render();
      expect(renderRadioOptionSpy).toHaveBeenCalledWith(tableOptionConfig, 0);
    });

    it('renders the user resource option when enabled', () => {
      AppConfig.indexUsers.enabled = true;
      renderRadioOptionSpy.mockClear();
      wrapper.instance().render();
      expect(renderRadioOptionSpy).toHaveBeenCalledWith(userOptionConfig, 1);
    });

    it('does not render user resource option when disabled', () => {
      AppConfig.indexUsers.enabled = false;
      renderRadioOptionSpy.mockClear();
      wrapper.instance().render();
      expect(renderRadioOptionSpy).not.toHaveBeenCalledWith(userOptionConfig);
    });
  })
});

describe('mapStateToProps', () => {
  let result;

  beforeAll(() => {
    result = mapStateToProps(globalState);
  });

  it('sets resource on the props', () => {
    expect(result.resource).toEqual(globalState.search.resource);
  });

  it('sets tables on the props', () => {
    expect(result.tables).toEqual(globalState.search.tables);
  });

  it('sets users on the props', () => {
    expect(result.users).toEqual(globalState.search.users);
  });

  it('sets dashboards on the props', () => {
    expect(result.dashboards).toEqual(globalState.search.dashboards);
  });
});

describe('mapDispatchToProps', () => {
  let result;
  let dispatch;
  beforeAll(() => {
    dispatch = jest.fn(() => Promise.resolve());
    result = mapDispatchToProps(dispatch);
  });

  it('sets setResource on the props', () => {
    expect(result.setResource).toBeInstanceOf(Function);
  });
});
