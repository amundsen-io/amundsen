// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as autosize from 'autosize';
import * as React from 'react';
import * as ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import LoadingSpinnerOverlay from 'components/LoadingSpinnerOverlay';
import { EditableSectionChildProps } from 'components/EditableSection';
import { logClick } from 'utils/analytics';
import {
  aiEnabled
} from 'config/config-utils';
import {
  CANCEL_BUTTON_TEXT,
  REFRESH_BUTTON_TEXT,
  REFRESH_MESSAGE,
  ADD_MESSAGE,
  UPDATE_BUTTON_TEXT,
} from './constants';

import './styles.scss';
import { getGPTResponse } from 'ducks/ai/reducer';
import { GetGPTResponse, GetGPTResponseRequest, GetGPTResponseResponse } from 'ducks/ai/types';
import { GPTResponse } from 'interfaces/AI';
import { PROPOSITION_LABEL } from 'features/Feedback/constants';

export interface StateFromProps {
  refreshValue?: string;
}

export interface DispatchFromProps {
  getLatestValue?: (onSuccess?: () => any, onFailure?: () => any) => void;
  onSubmitValue?: (
    newValue: string,
    onSuccess?: () => any,
    onFailure?: () => any
  ) => void;
  getGPTResponse?: (
    prompt: string,
    onSuccess?: (gptResponse: GetGPTResponseResponse) => any,
    onFailure?: (gptResponse: GetGPTResponseResponse) => any
  ) => GetGPTResponseRequest;
}

export interface ComponentProps {
  editable?: boolean;
  maxLength?: number;
  value?: string;
  gptResponse?: GPTResponse;
  allowDangerousHtml?: boolean;
}

export type EditableTextProps = ComponentProps &
  DispatchFromProps &
  StateFromProps &
  EditableSectionChildProps;

interface EditableTextState {
  value?: string;
  gptResponse?: GPTResponse;
  isDisabled: boolean;
  isAIEnabled: boolean;
  isGPTResponseLoading: boolean;
  aiError: boolean;
}

class EditableText extends React.Component<
  EditableTextProps,
  EditableTextState
> {
  readonly textAreaRef: React.RefObject<HTMLTextAreaElement>;
  readonly aiTextAreaRef: React.RefObject<HTMLTextAreaElement>;

  public static defaultProps: EditableTextProps = {
    editable: true,
    maxLength: 500,
    value: '',
    gptResponse: undefined
  };

  constructor(props: EditableTextProps) {
    super(props);
    this.textAreaRef = React.createRef<HTMLTextAreaElement>();
    this.aiTextAreaRef = React.createRef<HTMLTextAreaElement>();

    this.state = {
      isDisabled: false,
      isAIEnabled: false,
      value: props.value,
      gptResponse: undefined,
      isGPTResponseLoading: false,
      aiError: false
    };
  }

  componentDidUpdate(prevProps: EditableTextProps) {
    const { value: stateValue, isDisabled } = this.state;
    const {
      value: propValue,
      isEditing,
      refreshValue,
      getLatestValue
    } = this.props;

    // console.log(`refreshValue=${refreshValue}`)
    // console.log(`stateValue=${stateValue}`)
    // console.log(`propValue=${propValue}`)
    // console.log(`prevProps.value=${prevProps.value}`)

    if (prevProps.value !== propValue) {
      this.setState({ value: propValue });
    }
    else if (isEditing && !prevProps.isEditing) {
      const textArea = this.textAreaRef.current;

      if (textArea) {
        autosize(textArea);
        textArea.focus();
      }

      if (getLatestValue) {
        getLatestValue();
      }
    }
    else if ((refreshValue || stateValue) &&
              refreshValue !== stateValue &&
              !isDisabled) {
      // disable the component if a refresh is needed
      this.setState({ isDisabled: true });
    }
  }

  handleExitEditMode = (e: React.MouseEvent<HTMLButtonElement>) => {
    logClick(e, {
      label: 'Cancel Editable Text',
    });
    this.exitEditMode();
  };

  exitEditMode = () => {
    const { setEditMode } = this.props;

    setEditMode?.(false);
  };

  handleEnterEditMode = (e: React.MouseEvent<HTMLButtonElement>) => {
    const { setEditMode } = this.props;

    logClick(e, {
      label: 'Add Editable Text',
    });
    setEditMode?.(true);
  };

  handleRefreshText = (e: React.MouseEvent<HTMLButtonElement>) => {
    const { refreshValue } = this.props;
    const textArea = this.textAreaRef.current;

    this.setState({ value: refreshValue, isDisabled: false });
    logClick(e, {
      label: 'Refresh Editable Text',
    });

    if (textArea && refreshValue) {
      textArea.value = refreshValue;
      autosize.update(textArea);
    }
  };

  handleUpdateText = (e: React.MouseEvent<HTMLButtonElement>) => {
    const { setEditMode, onSubmitValue } = this.props;
    const newValue = this.textAreaRef.current?.value;

    const onSuccessCallback = () => {
      setEditMode?.(false);
      this.setState({ value: newValue });
    };
    const onFailureCallback = () => {
      this.exitEditMode();
    };

    logClick(e, {
      label: 'Update Editable Text',
    });

    if (newValue) {
      onSubmitValue?.(newValue, onSuccessCallback, onFailureCallback);
    }
  };

  handleAIEnabledChange = (event) => {
    this.setState({ isAIEnabled: event.target.checked});
  };

  handleGenerateDescription = (e: React.MouseEvent<HTMLButtonElement>) => {
    const { getGPTResponse } = this.props;

    const onSuccessCallback = (gptResponse: GetGPTResponseResponse) => {
      this.setState({ isGPTResponseLoading: false, aiError: false});
      if (gptResponse.payload.gptResponse && gptResponse.payload.gptResponse.message && gptResponse.payload.gptResponse.message.content) {
        const textArea = this.textAreaRef.current;
        if (textArea) {
          textArea.value = gptResponse.payload.gptResponse.message.content
          autosize.update(textArea);
        }
      }
    };
    const onFailureCallback = (gptResponse: GetGPTResponseResponse) => {
      this.setState({ isGPTResponseLoading: false, aiError: true});
    };

    if (this.aiTextAreaRef.current && this.aiTextAreaRef.current.value) {
      getGPTResponse?.(this.aiTextAreaRef.current.value, onSuccessCallback, onFailureCallback);
      this.setState({ isGPTResponseLoading: true, aiError: false});
    }
  };

  render() {
    const { isEditing, editable, maxLength, allowDangerousHtml } = this.props;
    const { value = '', isDisabled, isAIEnabled, isGPTResponseLoading, aiError } = this.state;

    if (isGPTResponseLoading) {
      return (
        <LoadingSpinnerOverlay isLoading={true} />
      )
    }

    if (!isEditing) {
      return (
        <div className="editable-text">
          <div className="markdown-wrapper">
            <ReactMarkdown
              allowDangerousHtml={!!allowDangerousHtml}
              plugins={[remarkGfm]}
            >
              {value}
            </ReactMarkdown>
          </div>
          {editable && !value && (
            <button
              className="edit-link btn btn-link"
              style={{ fontFamily: 'IBM Plex Mono'}}
              onClick={this.handleEnterEditMode}
              data-type="add-editable-text"
              type="button"
            >
              {ADD_MESSAGE}
            </button>
          )}
        </div>
      );
    }

    return (
      <div className="editable-text">
        {/* Conditionally render the additional textarea and button */}
          {isAIEnabled && (
            <>
              <textarea
                className="editable-textarea"
                rows={2}
                maxLength={maxLength}
                ref={this.aiTextAreaRef}
                placeholder="Enter prompt here..."
                disabled={isDisabled}
                aria-label="Editable text area"
              />
              <button
                className="btn btn-primary update-button"
                onClick={this.handleGenerateDescription}
                type="button"
                data-type="update-editable-text"
              >
                Generate Description
              </button>
            </>
          )}
          {aiError && (
            <h2 className="label label-danger refresh-message">
              There was a problem accessing the AI service. Plesae try again later.
            </h2>
          )}
        {aiEnabled() && (
          <div className="editable-textarea-controls">
            <label>
              <input
                type="checkbox"
                checked={isAIEnabled}
                onChange={this.handleAIEnabledChange}
              />
              Enable AI
            </label>
          </div>
        )}
        <textarea
          className="editable-textarea"
          rows={2}
          maxLength={maxLength}
          ref={this.textAreaRef}
          placeholder="Enter description here..."
          defaultValue={value}
          disabled={isDisabled}
          aria-label="Editable text area"
        />
        <div className="editable-textarea-controls">
          {isDisabled && (
            <>
              <h2 className="label label-danger refresh-message">
                {REFRESH_MESSAGE}
              </h2>
              <button
                className="btn btn-primary refresh-button"
                onClick={this.handleRefreshText}
                data-type="refresh-editable-text"
                type="button"
              >
                <img className="icon icon-refresh" alt="" />
                {REFRESH_BUTTON_TEXT}
              </button>
            </>
          )}
          {!isDisabled && (
            <button
              className="btn btn-primary update-button"
              onClick={this.handleUpdateText}
              type="button"
              data-type="update-editable-text"
            >
              {UPDATE_BUTTON_TEXT}
            </button>
          )}
          <button
            className="btn btn-default cancel-button"
            onClick={this.handleExitEditMode}
            type="button"
            data-type="cancel-editable-text"
          >
            {CANCEL_BUTTON_TEXT}
          </button>
        </div>
      </div>
    );
  }
}

export default EditableText;

