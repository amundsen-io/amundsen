import * as React from 'react';
import moment from 'moment-timezone';

import './styles.scss';

import { Watermark } from 'interfaces';

interface WatermarkLabelProps {
  watermarks: Watermark[];
}

class WatermarkLabel extends React.Component<WatermarkLabelProps> {

  constructor(props) {
    super(props);
    this.getWatermarksLabel = this.getWatermarksLabel.bind(this);
  }

  render() {
    return (
        <div className="watermark-label">{this.getWatermarksLabel(this.props.watermarks)}</div>
      )
  }

  getWatermarksLabel(watermarks: Watermark[]) {
    const low = watermarks.find((wtm) => wtm.watermark_type === "low_watermark");
    const high = watermarks.find((wtm) => wtm.watermark_type === "high_watermark");
    if (low === undefined && high === undefined) {
      return "Non Partitioned Table. Data available for all dates."
    }
    return [low, high].map((wtm) => {
      return moment(wtm.partition_value, "YYYY-MM-DD").format("MMM DD, YYYY");
    }).join(" – ");
  }
}

export default WatermarkLabel;
