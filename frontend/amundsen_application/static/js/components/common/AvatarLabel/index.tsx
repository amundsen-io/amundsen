import * as React from 'react';
import * as Avatar from 'react-avatar';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

export interface AvatarLabelProps {
  label?: string;
  src?: string;
}

const AvatarLabel: React.SFC<AvatarLabelProps> = ({ label, src }) => {
  return (
    <div className="avatar-label-component">
      <Avatar name={label} src={src} size={24} round={true} />
      <span className="avatar-label body-2">{ label }</span>
    </div>
  );
};

AvatarLabel.defaultProps = {
  label: '',
  src: ''
};

export default AvatarLabel;
