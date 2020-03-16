import * as React from 'react';

import './styles.scss';

export interface EditableSectionProps {
  title: string;
  readOnly?: boolean;
}

interface EditableSectionState {
  isEditing: boolean;
}

export interface EditableSectionChildProps {
  isEditing?: boolean;
  setEditMode?: (isEditing: boolean) => void;
}

export class EditableSection extends React.Component<EditableSectionProps, EditableSectionState> {
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

  render() {
    const childrenWithProps = React.Children.map(this.props.children, child => {
      if (!React.isValidElement(child)) {
        return child;
      }
      return React.cloneElement(child, {
        isEditing: this.state.isEditing,
        setEditMode: this.setEditMode,
      });
    });

    return (
      <section className="editable-section">
        <div className="section-title title-3">
          { EditableSection.convertText(this.props.title) }
          {
            !this.props.readOnly &&
            <button className={"btn btn-flat-icon edit-button" + (this.state.isEditing? " active": "")} onClick={ this.toggleEdit }>
              <img className={"icon icon-small icon-edit" + (this.state.isEditing? " icon-color" : "")} />
            </button>
          }
        </div>
        { childrenWithProps }
      </section>
    );
  }
}
