import React, { ReactNode } from 'react';

type BlockProps = {
  children: ReactNode;
  title: string;
  text?: string | ReactNode;
};

const StorySection: React.FC<BlockProps> = ({
  children,
  text,
  title,
}: BlockProps) => (
  <div style={{ padding: '2em 2em 1em', maxWidth: 600 }}>
    <h1 className="text-headline-w1">{title}</h1>
    {text && <p className="text-body-w1">{text}</p>}
    <div style={{ paddingTop: '1em' }}>{children}</div>
  </div>
);

export default StorySection;
