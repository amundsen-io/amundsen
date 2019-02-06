import * as React from 'react';
import ReactDOM from 'react-dom';
import serialize from 'form-serialize';

import ConfirmDeleteButton from '../ConfirmDeleteButton';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

export interface DispatchFromProps {
  onAddItem: (value: string, onSuccess?: () => any, onFailure?: () => any) => void;
  onDeleteItem: (value: string, onSuccess?: () => any, onFailure?: () => any) => void;
}

export interface ComponentProps {
  readOnly: boolean;
  listItemProps?: object[];
  listItemPropTypes: {name: string, property: string, type: string}[];
  listItemRenderer: (props: object) => JSX.Element;
}

type EditableListProps = ComponentProps & DispatchFromProps;

interface EditableListState {
  readOnly: boolean;
  listItemProps: object[];
}

class EditableList extends React.Component<EditableListProps, EditableListState> {
  public static defaultProps: EditableListProps = {
    readOnly: true,
    listItemProps: [],
    listItemPropTypes: [],
    listItemRenderer: null,
    onAddItem: null,
    onDeleteItem: null,
  };

  constructor(props) {
    super(props);

    this.state = {
      readOnly: props.readOnly,
      listItemProps: props.listItemProps,
    };
  }

  deleteItem = (index) => {
    if (!this.state.readOnly && this.state.listItemProps.length > 1) {
      const onSuccessCallback = () => {
        const newListItemProps = this.state.listItemProps.filter((item, i) => i !== index);
        this.setState({ listItemProps: newListItemProps });
      };

      this.props.onDeleteItem(this.state.listItemProps[index]['label'], onSuccessCallback, null);
    }
  }

  addItem = (event) => {
    event.preventDefault();
    const formElement = event.target;
    const props = serialize(formElement, { hash: true });
    const onSuccessCallback = () => {
      const newListItemProps = this.state.listItemProps.concat([props]);
      formElement.reset();
      this.setState({ listItemProps: newListItemProps });
    }

    this.props.onAddItem(props.label, onSuccessCallback, null);
  }

  componentWillReceiveProps(newProps) {
    if (newProps.readOnly !== this.state.readOnly) {
      this.setState({ readOnly: newProps.readOnly })
    }
  }

  render() {
    if (this.state.readOnly && this.state.listItemProps.length === 0) {
      return ( <label className="m-auto">No entries exist</label> );
    }

    const renderDeleteButton = !this.state.readOnly && this.state.listItemProps.length > 1;
    const listGroup = this.state.listItemProps.map((props, index) => {
      return (
        <li key={`list-item:${index}`}>
          { React.createElement(this.props.listItemRenderer, props) }
          {
            renderDeleteButton &&
            /* tslint:disable - TODO: Investigate jsx-no-lambda rule */
            <ConfirmDeleteButton onConfirmHandler={() => this.deleteItem(index)}/>
            /* tslint:enable */
          }
        </li>
      )
    });

    return (
      <div className='editable-list-component'>
        {
          this.state.listItemProps.length > 0 &&
          <ul className='component-list'>
            { listGroup }
          </ul>
        }
        {
          !this.state.readOnly &&
          <div>
            <label className='component-form-title'>Add a new entry</label>
            <form className='component-form' onSubmit={this.addItem}>
              {
                this.props.listItemPropTypes.map((entry, index) => {
                  return (
                    <div className="component-form-group" key={`${entry.property}:input`}>
                      <label className="component-form-label" htmlFor={entry.property}>{entry.name}:</label>
                      <input id={entry.property} name={entry.property} type={entry.type} autoFocus={index === 0}/>
                    </div>
                  )
                })
              }
              <button className="add-button" type="submit" aria-label="Add Item">
                <span aria-hidden="true">&#43;</span>
              </button>
            </form>
          </div>
        }
      </div>
    );
  }
}

export default EditableList;
