import * as React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { Modal } from 'react-bootstrap';
import { components } from 'react-select';
import CreatableSelect from 'react-select/lib/Creatable';

import { GlobalState } from 'ducks/rootReducer';
import { getAllTags } from 'ducks/allTags/reducer';
import { GetAllTagsRequest } from 'ducks/allTags/types';
import { updateTags } from 'ducks/tableMetadata/tags/reducer';
import { UpdateTagsRequest } from 'ducks/tableMetadata/types';

import TagInfo from "../TagInfo";
import { Tag, UpdateMethod, UpdateTagData } from 'interfaces';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

const VALID_TAG_REGEXP = new RegExp(/^([a-z0-9_]+)$/);
const BATCH_EDIT_TAG_OPTION  = 'amundsen_batch_edit';

const FILTER_COMMON_TAGS =
  (otherArray) => (current) => otherArray.filter((other) => (other.tag_name === current.tag_name)).length === 0;

enum BatchEditState {
  CURRENT = 'CURRENT',
  DELETE = 'DELETE',
  PUT = 'PUT',
}

export interface StateFromProps {
  allTags: Tag[];
  isLoading: boolean;
  tags: Tag[];
}

export interface DispatchFromProps {
  updateTags: (tagArray: UpdateTagData[]) => UpdateTagsRequest;
  getAllTags: () => GetAllTagsRequest;
}

export interface ComponentProps {
  readOnly: boolean;
}

type TagInputProps = StateFromProps & DispatchFromProps & ComponentProps;

interface TagInputState {
  allTags: Tag[];
  isLoading: boolean;
  readOnly: boolean;
  showModal: boolean;
  tags: Tag[];
}

class TagInput extends React.Component<TagInputProps, TagInputState> {
  private batchEditSet: Map<string, BatchEditState> | {};

  public static defaultProps: TagInputProps = {
    allTags: [],
    getAllTags: () => void(0),
    isLoading: false,
    readOnly: true,
    tags: undefined,
    updateTags: () => void(0),
  };

  static getDerivedStateFromProps(nextProps, prevState) {
    const { allTags, isLoading, readOnly, tags } = nextProps;
    return { ...prevState, allTags, isLoading, readOnly, tags };
  }

  constructor(props) {
    super(props);
    this.state = {
      allTags: props.allTags,
      isLoading: props.isLoading,
      readOnly: props.readOnly,
      showModal: false,
      tags: props.tags,
    };
  }

  componentDidMount() {
    this.props.getAllTags();
  }

  handleClose = () => {
    this.batchEditSet = {};
    this.setState({ showModal: false });
  }

  handleShow = () => {
    this.batchEditSet = {};
    this.state.tags.map((tag) => {
      this.batchEditSet[tag.tag_name] = BatchEditState.CURRENT;
    });
    this.setState({ showModal: true });
  }

  handleSaveModalEdit = () => {
    const tagArray = Object.keys(this.batchEditSet).reduce((previousValue, tag) => {
      const action = this.batchEditSet[tag];
      if (action === BatchEditState.DELETE) {
        previousValue.push({'methodName': UpdateMethod.DELETE, 'tagName': tag});
      }
      else if (action === BatchEditState.PUT) {
        previousValue.push({'methodName': UpdateMethod.PUT, 'tagName': tag});
      }
      return previousValue;
    }, []);
    this.props.updateTags(tagArray);
    this.handleClose();
  };

  generateCustomOptionStyle(provided, state) {
    // https://react-select.com/props#api
    const isSeeAll = state.value === BATCH_EDIT_TAG_OPTION ;
    return {
      ...provided,
      color: isSeeAll ? 'grey' : 'inherit',
      fontStyle: isSeeAll ? 'italic' : 'inherit'
    };
  }

  isValidNewOption(inputValue, selectValue, selectOptions) {
    // https://react-select.com/props#api
    return VALID_TAG_REGEXP.test(inputValue);
  }

  mapTagsToReactSelectAPI(tagArray) {
    return tagArray.map((tag) => {
      return {'value': tag.tag_name, 'label': tag.tag_name };
    })
  }

  mapOptionsToReactSelectAPI(tagArray) {
    return [{'value': BATCH_EDIT_TAG_OPTION , 'label': 'Select From All Tags...'}].concat(this.mapTagsToReactSelectAPI(tagArray));
  }

  noOptionsMessage(inputValue) {
    // https://react-select.com/props#api
    if (VALID_TAG_REGEXP.test(inputValue.inputValue)) {
      return "Tag already exists.";
    }
    return "Valid characters include a-z, 0-9, and '_'.";
  }

  onChange = (currentTags, actionPayload) => {
    // https://react-select.com/props#api
    const actionType = actionPayload.action;
    let tag;
    if (actionType === "select-option" || actionType === "create-option") {
      tag = (actionType === "select-option") ? actionPayload.option.value : currentTags[currentTags.length - 1]['value'];
      if (tag === BATCH_EDIT_TAG_OPTION ) {
        currentTags.pop();
        this.handleShow();
      }
      else {
        this.props.updateTags([{'methodName': UpdateMethod.PUT, 'tagName': tag}]);
      }
    }
    else if (actionType === "remove-value" || actionType === "pop-value") {
      tag = actionPayload.removedValue.value;
      this.props.updateTags([{'methodName': UpdateMethod.DELETE, 'tagName': tag}]);
    }
  };

  preventDeleteOnBackSpace(event) {
    if (event.keyCode === 8 && event.target.value.length === 0){
      event.preventDefault();
    }
  }

  toggleTag = (event, tagName) => {
    const element = event.currentTarget;
    element.classList.contains('selected') ? element.classList.remove('selected') : element.classList.add('selected');

    if (!this.batchEditSet.hasOwnProperty(tagName)) {
      this.batchEditSet[tagName] = BatchEditState.PUT;
    }
    else if (this.batchEditSet[tagName] === BatchEditState.PUT) {
      delete this.batchEditSet[tagName];
    }
    else if (this.batchEditSet[tagName] === BatchEditState.CURRENT) {
      this.batchEditSet[tagName] = BatchEditState.DELETE;
    }
    else if (this.batchEditSet[tagName] === BatchEditState.DELETE) {
      this.batchEditSet[tagName] = BatchEditState.CURRENT;
    }
  };

  renderTagBlob(tagArray, keyPrefix, className) {
    return tagArray.map((tag) => {
      const tagName = tag.tag_name;
      const labelProps = {
        'children': tagName,
        'data': {'value': tagName, 'label': tagName },
        'innerProps': {'className': 'multi-value-label'},
      };
      const updateTag = (event) => {
        this.toggleTag(event, tagName);
      };
      return  (
        <div onClick={updateTag} key={`${keyPrefix}:${tagName}`} className={className}>
          <components.MultiValueContainer>
            <components.MultiValueLabel {...labelProps} />
          </components.MultiValueContainer>
        </div>
      )
    })
  }

  renderModalBody() {
    return (
        <div className=''>
          <p className=''>Click on a tag to add/remove</p>
          <div className='tag-blob'>
            { this.renderTagBlob(this.state.tags, 'current', 'multi-value-container selected') }
            { this.renderTagBlob(this.state.allTags.filter(FILTER_COMMON_TAGS(this.state.tags)), 'existing', 'multi-value-container') }
          </div>
        </div>
    )
  }

  render() {
    // https://react-select.com/props#api
    const componentOverides = this.state.readOnly ? {
      DropdownIndicator: () => { return null },
      IndicatorSeparator: () => { return null },
      MultiValueRemove: () => { return null },
    } : {
      DropdownIndicator: () => { return null },
      IndicatorSeparator: () => { return null },
    };

    let tagBody;
    if (this.state.readOnly) {
      tagBody = this.state.tags.map((tag, index) => <TagInfo data={tag} key={index}/>)
    } else {
      tagBody = (
        <CreatableSelect
          autoFocus={true}
          className="basic-multi-select"
          classNamePrefix="amundsen"
          components={componentOverides}
          isClearable={false}
          isDisabled={this.state.isLoading}
          isLoading={this.state.isLoading}
          isMulti={true}
          isValidNewOption={this.isValidNewOption}
          name="tags"
          noOptionsMessage={this.noOptionsMessage}
          onChange={this.onChange}
          onKeyDown={this.preventDeleteOnBackSpace}
          options={this.mapOptionsToReactSelectAPI(this.state.allTags)}
          placeholder='Add a new tag'
          styles={{
            multiValueLabel: (provided) => ({
              ...provided,
              fontSize: '14px',
              height: '30px',
              lineHeight: '24px',
              width: '100%',
            }),
            option: this.generateCustomOptionStyle
          }}
          value={this.mapTagsToReactSelectAPI(this.state.tags)}
        />
      );
    }

    return (
      <div className='tag-input'>
        { tagBody }
        <Modal className='tag-input-modal' show={this.state.showModal} onHide={this.handleClose}>
          <Modal.Header className="text-center" closeButton={false}>
            <Modal.Title>Add/Remove Tags</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            {this.renderModalBody()}
          </Modal.Body>
          <Modal.Footer>
            <button type="button" className="btn btn-default" onClick={this.handleClose}>Cancel</button>
            <button type="button" className="btn btn-primary" onClick={this.handleSaveModalEdit}>Save</button>
          </Modal.Footer>
        </Modal>
      </div>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => {
  return {
    allTags: state.allTags.allTags,
    isLoading: state.allTags.isLoading || state.tableMetadata.tableTags.isLoading,
    tags: state.tableMetadata.tableTags.tags,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ getAllTags, updateTags } , dispatch);
};

export default connect<StateFromProps, DispatchFromProps, ComponentProps>(mapStateToProps, mapDispatchToProps)(TagInput);
