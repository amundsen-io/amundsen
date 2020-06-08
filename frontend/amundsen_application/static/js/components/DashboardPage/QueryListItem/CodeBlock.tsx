import * as React from 'react';
import { CopyBlock, atomOneLight } from 'react-code-blocks';

const LANGUAGE = "sql";

const CodeBlock = ({text}) => {
  return (
    <CopyBlock
      text={text}
      language={LANGUAGE}
      theme={atomOneLight}
      showLineNumbers={false}
      wrapLines={true}
      codeBlock={true}
    />
  );
}

export default CodeBlock;
