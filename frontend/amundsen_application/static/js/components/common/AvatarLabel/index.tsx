import * as React from 'react';
import * as Avatar from 'react-avatar';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

export interface AvatarLabelProps {
  avatarClass?: string;
  labelClass?: string;
  label?: string;
  src?: string;
}

const AvatarLabel: React.SFC<AvatarLabelProps> = ({ avatarClass, labelClass, label, src }) => {
  return (
    <div className="avatar-label-component">
      <Avatar
        className={avatarClass}
        name={label}
        src={src}
        size={24}
        round={true}
      />
      <span className={`avatar-label body-2 ${labelClass}`}>{ label }</span>
    </div>
  );
};

AvatarLabel.defaultProps = {
  labelClass: 'text-secondary',
  label: '',
  src: ''
};

export default AvatarLabel;
