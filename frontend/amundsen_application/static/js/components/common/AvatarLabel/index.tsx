import * as React from 'react';
import Avatar from 'react-avatar';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

export interface AvatarLabelProps {
  label?: string;
  src?: string;
}

const AvatarLabel: React.SFC<AvatarLabelProps> = ({ label, src }) => {
  return (
    <div className='avatar-label-component'>
      <div className='component-avatar'>
        <Avatar name={label} src={src} size={25} round={true} />
      </div>
      <label className='component-label'>{label}</label>
    </div>
  );
};

AvatarLabel.defaultProps = {
  label: '',
  src: ''
};

export default AvatarLabel;
