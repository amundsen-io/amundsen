import * as React from 'react';
import { shallow } from 'enzyme';

import {EditableSection, EditableSectionProps} from '../';
import TagInput from 'components/Tags/TagInput';


describe("EditableSection", () => {
  const setup = (propOverrides?: Partial<EditableSectionProps>, children?) => {
    const props = {
      title: "defaultTitle",
      readOnly: false,
      ...propOverrides,
    };
    const wrapper = shallow<EditableSection>(<EditableSection {...props} >{ children }</EditableSection>)
    return { wrapper, props };
  };

  describe("setEditMode", () => {
    const { wrapper, props } = setup();

    it("Enters edit mode after calling setEditMode(true)", () => {
      wrapper.instance().setEditMode(true);
      expect(wrapper.state().isEditing).toBe(true);
    });

    it("Exits edit mode after calling setEditMode(false)", () => {
      wrapper.instance().setEditMode(false);
      expect(wrapper.state().isEditing).toBe(false);
    });
  });

  describe("toggleEdit", () => {
    const { wrapper, props } = setup();
    const initialEditMode = wrapper.state().isEditing;

    it("Toggles the edit mode from the after each call", () => {
      // First call
      wrapper.instance().toggleEdit();
      expect(wrapper.state().isEditing).toBe(!initialEditMode);

      // Second call
      wrapper.instance().toggleEdit();
      expect(wrapper.state().isEditing).toBe(initialEditMode);
    });
  });

  describe("render", () => {
    const customTitle = "custom title";
    const { wrapper, props } = setup({ title: customTitle }, <TagInput/>);

    it("sets the title from a prop", () => {
      expect(wrapper.find(".section-title").text()).toBe("Custom Title");
    });

    it("renders children with additional props", () => {
      const childProps = wrapper.find(TagInput).props();
      expect(childProps).toMatchObject({
        isEditing: wrapper.state().isEditing,
        setEditMode: wrapper.instance().setEditMode
      });
    });

    it("renders children as-is for non-react elements", () => {
      const child = "non-react-child";
      const { wrapper } = setup(null, child);
      expect(wrapper.childAt(1).text()).toBe(child);
    });

    it("renders button when readOnly=false", () => {
      expect(wrapper.find(".edit-button").length).toEqual(1);
    });

    it("renders does not add button when readOnly=true", () => {
      const { wrapper } = setup({readOnly: true}, <TagInput/>);
      expect(wrapper.find(".edit-button").length).toEqual(0);
    });

    it('renders modifies title to have no underscores', () => {
      expect(EditableSection.convertText("testing_a123_b456 c789")).toEqual("Testing A123 B456 C789")
    })
  });
});
