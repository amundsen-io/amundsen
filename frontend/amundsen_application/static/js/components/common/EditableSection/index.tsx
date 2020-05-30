import * as React from 'react';
import { OverlayTrigger, Popover } from 'react-bootstrap';

import * as Constants from './constants';

import './styles.scss';

export interface EditableSectionProps {
  title: string;
  readOnly?: boolean;
  /* Should be used when readOnly=true to prompt users with a relevant explanation for the given use case */
  editText?: string;
  /* Should be used when readOnly=true to link to the source where users can edit the given metadata */
  editUrl?: string;
}

interface EditableSectionState {
  isEditing: boolean;
}

export interface EditableSectionChildProps {
  isEditing?: boolean;
  setEditMode?: (isEditing: boolean) => void;
}

export class EditableSection extends React.Component<EditableSectionProps, EditableSectionState> {
  static defaultProps: Partial<EditableSectionProps> = {
    editText: Constants.EDIT_TEXT,
  };

  constructor(props) {
    super(props);

    this.state = {
      isEditing: false,
    }
  }

  setEditMode = (isEditing: boolean) => {
    this.setState({ isEditing });
  };

  toggleEdit = () => {
    this.setState({ isEditing: !this.state.isEditing });
  };

  static convertText(str: string): string {
    return str.split(new RegExp('[\\s+_]')).map(x => x.charAt(0).toUpperCase() + x.slice(1).toLowerCase()).join(" ");
  }

  renderButton = (): React.ReactNode => {
     return (
       <button className={`btn btn-flat-icon edit-button ${(this.state.isEditing ? 'active': '')}`} onClick={ this.toggleEdit }>
         <img className={`icon icon-small icon-edit ${(this.state.isEditing ? 'icon-color' : '')}`} />
       </button>
     );
  };

  renderReadOnlyButton = (): React.ReactNode => {
    const { editText, editUrl } = this.props;
    const popoverHoverFocus = (<Popover id="popover-trigger-hover-focus">{ editText }</Popover>);

    if (!editUrl) {
      return null;
    }
    return (
      <OverlayTrigger
       trigger={["hover", "focus"]}
       placement="top"
       overlay={popoverHoverFocus}
      >
        <a className="btn btn-flat-icon-dark edit-button" href={ editUrl } target="_blank" rel="noopener noreferrer">
          <img className="icon icon-small icon-edit" />
        </a>
      </OverlayTrigger>
    );
  };

  render() {
    const { title, readOnly = false } = this.props;
    const childrenWithProps = !readOnly ? React.Children.map(this.props.children, child => {
      if (!React.isValidElement(child)) {
        return child;
      }
      return React.cloneElement(child, {
        isEditing: this.state.isEditing,
        setEditMode: this.setEditMode,
      });
    }) : this.props.children;

    return (
      <section className="editable-section">
        <div className="section-title title-3">
          { EditableSection.convertText(title) }
          { !readOnly ? this.renderButton() : this.renderReadOnlyButton() }
        </div>
        { childrenWithProps }
      </section>
    );
  }
}

export default EditableSection;
