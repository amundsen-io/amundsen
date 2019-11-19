import * as React from 'react';
import * as moment from 'moment-timezone';

import './styles.scss';

import { Watermark } from 'interfaces';
import {
  HIGH_WATERMARK_LABEL,
  NO_WATERMARK_LINE_1, NO_WATERMARK_LINE_2, LOW_WATERMARK_LABEL,
  WATERMARK_DISPLAY_FORMAT,
  WATERMARK_INPUT_FORMAT,
  WatermarkType
} from './constants';

export interface WatermarkLabelProps {
  watermarks: Watermark[];
}

class WatermarkLabel extends React.Component<WatermarkLabelProps> {
  constructor(props) {
    super(props);
  }

  formatWatermarkDate = (dateString: string) => {
    return moment(dateString, WATERMARK_INPUT_FORMAT).format(WATERMARK_DISPLAY_FORMAT);
  };

  getWatermarkValue = (type: WatermarkType) => {
    const watermark = this.props.watermarks.find((watermark: Watermark) => watermark.watermark_type === type);
    return watermark && watermark.partition_value || null;
  };

  renderWatermarkInfo = (low: string, high: string) => {
    if (low === null && high === null) {
      return (
        <div className="body-2">
          { NO_WATERMARK_LINE_1 }
          <br/>
          { NO_WATERMARK_LINE_2 }
        </div>
      );
    }

    return (
      <>
        <div className="range-labels body-2">
          { LOW_WATERMARK_LABEL }
          <br/>
          { HIGH_WATERMARK_LABEL }
        </div>
        <div className="range-dates body-2">
          { low && this.formatWatermarkDate(low) }
          <br/>
          { high && this.formatWatermarkDate(high) }
        </div>
      </>
    );
  };

  render() {
    const low = this.getWatermarkValue(WatermarkType.LOW);
    const high = this.getWatermarkValue(WatermarkType.HIGH);

    return (
      <div className="watermark-label">
        <img className="range-icon" src="/static/images/watermark-range.png"/>
        { this.renderWatermarkInfo(low, high) }
      </div>
    );
  }
}

export default WatermarkLabel;
