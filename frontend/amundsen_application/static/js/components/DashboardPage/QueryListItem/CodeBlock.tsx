// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { CopyBlock, atomOneLight } from 'react-code-blocks';

const LANGUAGE = 'sql';

type CodeBlockProps = {
  text: string;
};

const CodeBlock: React.FC<CodeBlockProps> = ({ text }: CodeBlockProps) => {
  return (
    <CopyBlock
      text={text}
      language={LANGUAGE}
      theme={atomOneLight}
      showLineNumbers={false}
      wrapLines
      codeBlock
    />
  );
};

export default CodeBlock;
