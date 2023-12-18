// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { EditableSectionChildProps } from 'components/EditableSection';

import { logClick } from 'utils/analytics';

export interface StateFromProps {
  refreshValue?: string;
  options: SelectOption[];
  defaultOption?: string;
}

export interface DispatchFromProps {
  onUpdateValue?: (
    newValue: string,
    onSuccess?: () => any,
    onFailure?: () => any
  ) => void;
  onDeleteValue?: (
    onSuccess?: () => any,
    onFailure?: () => any
  ) => void;
}

export interface ComponentProps {
  editable?: boolean;
  value?: string;
}

export enum SelectOptionAction {
  UPDATE = 'update',
  DELETE = 'delete'
}

export interface SelectOption {
  option: string;
  action: SelectOptionAction;
}

export type EditableSelectProps = ComponentProps &
  DispatchFromProps &
  StateFromProps &
  EditableSectionChildProps;

interface EditableSelectState {
  value?: string;
  isDisabled: boolean;
}

class EditableSelect extends React.Component<
  EditableSelectProps,
  EditableSelectState
> {
  public static defaultProps: EditableSelectProps = {
    editable: true,
    value: '',
    options: [],
  };

  constructor(props: EditableSelectProps) {
    super(props);

    this.state = {
      isDisabled: false,
      value: props.value,
    };
  }

  componentDidUpdate(prevProps: EditableSelectProps) {
    const { value: stateValue, isDisabled } = this.state;
    const {
      value: propValue,
      isEditing,
      refreshValue
    } = this.props;

    if (prevProps.value !== propValue) {
      this.setState({ value: propValue });
    }
    else if (isEditing && !prevProps.isEditing) {
    }
    else if ((refreshValue || stateValue) &&
              refreshValue !== stateValue &&
              !isDisabled) {
      // disable the component if a refresh is needed
      // this.setState({ isDisabled: true });
    }
  }

  setSelectValue = (value, action) => {
    const { setEditMode, onUpdateValue, onDeleteValue, options } = this.props;
    const newValue = value;

    const onSuccessCallback = () => {
      //setEditMode?.(false);
      this.setState({ value: newValue });
    };
    const onFailureCallback = () => {
      //this.exitEditMode();
      console.log("select option failed")
    };

    if (newValue) {
      if (action == SelectOptionAction.UPDATE) {
        onUpdateValue?.(newValue, onSuccessCallback, onFailureCallback);
      }
      else if (action == SelectOptionAction.DELETE) {
        onDeleteValue?.(onSuccessCallback, onFailureCallback);
      }
    }
  };

  render() {
    const { isEditing, editable, options, defaultOption } = this.props;
    const { value = '', isDisabled } = this.state;

    return (
        <select
            value={value == null && defaultOption != null ? defaultOption.toLowerCase() : value}
            onChange={e => this.setSelectValue(e.target.value, e.target.options[e.target.selectedIndex].getAttribute('data-action'))}
            id="update-table-frequency-dropdown"
            disabled={isDisabled || !editable} // If you want to control the disabled state of the dropdown
        >
            {options.map(option => (
                <option key={option.option} value={option.option.toLowerCase()} data-action={option.action}>
                    {option.option.charAt(0).toUpperCase() + option.option.slice(1)}
                </option>
            ))}
        </select>
    );
  }
}

export default EditableSelect;

