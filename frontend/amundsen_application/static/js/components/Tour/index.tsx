// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import Joyride, { Step, Props, CallBackProps, STATUS } from 'react-joyride';
import { useLocalStorage, writeStorage } from '@rehooks/local-storage';

import './styles.scss';

const SKIP_BUTTON_TEXT = 'Dismiss';
const LAST_BUTTON_TEXT = 'Done';
const DEFAULT_LOCAL_STORAGE_KEY = 'tourFeature';
const PAGE_LOAD_DELAY = 3000;
const GRAY_100 = '#292936';
const GRAY_70 = '#515167';
const INDIGO_60 = '#665AFF';

const DEFAULT_CONFIGURATION = {
  continuous: true,
  showProgress: false,
  scrollToFirstStep: true,
  showSkipButton: true,
  disableScrolling: true,
  styles: {
    options: {
      textColor: GRAY_100,
      primaryColor: INDIGO_60,
      overlayColor: GRAY_70,
      zIndex: 1000,
    },
    buttonSkip: {
      color: INDIGO_60,
      fontSize: 16,
    },
  },
  locale: {
    skip: SKIP_BUTTON_TEXT,
    last: LAST_BUTTON_TEXT,
  },
};

export interface TourProps {
  /**
   * Steps of the tour
   */
  steps: Step[];
  /**
   * Whether the Tour component should be run, defaults to true
   */
  run?: boolean;
  /**
   * Options to overrides our defaults
   */
  configurationOverrides?: Partial<Props>;
  /**
   * Callback to call when the tour finishes
   */
  onTourEnd?: () => void;
  /**
   * Whether the tour will trigger automatically when first loaded (based on local storage)
   */
  triggersOnFirstView?: boolean;
  /**
   * Identifier for the local storage key (advisable when triggersOnFirstView is true)
   */
  triggerFlagId?: string;
}

export const Tour: React.FC<TourProps> = ({
  steps,
  configurationOverrides,
  run = true,
  triggersOnFirstView = false,
  triggerFlagId = DEFAULT_LOCAL_STORAGE_KEY,
  onTourEnd,
}) => {
  const configuration = {
    ...DEFAULT_CONFIGURATION,
    ...configurationOverrides,
  };
  const [runTourOnFirstView, setRunTourOnFirstView] = React.useState(false);
  const [hasSeenTour] = useLocalStorage<boolean>(triggerFlagId);

  // Logic for automatic tour run when first landed
  React.useEffect(() => {
    let loadDelayTimeoutId: NodeJS.Timeout;

    if (triggersOnFirstView && !hasSeenTour) {
      // We introduce a delay to account for the page load time
      loadDelayTimeoutId = setTimeout(() => {
        setRunTourOnFirstView(true);
      }, PAGE_LOAD_DELAY);
      writeStorage(triggerFlagId, true);
    }

    return () => {
      if (loadDelayTimeoutId) {
        clearTimeout(loadDelayTimeoutId);
      }
    };
    // Disabling exhaustive-deps as listening for hasSeenTour would make it impossible to test the feature
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [triggersOnFirstView, triggerFlagId]);

  const handleCallback = (data: CallBackProps) => {
    const { status } = data;
    const finishedStatuses: string[] = [STATUS.FINISHED, STATUS.SKIPPED];

    if (finishedStatuses.includes(status)) {
      setRunTourOnFirstView(false);
      if (onTourEnd) {
        onTourEnd();
      }
    }
  };

  return (
    <Joyride
      run={run || runTourOnFirstView}
      steps={steps}
      callback={handleCallback}
      // eslint-disable-next-line react/jsx-props-no-spreading
      {...configuration}
    />
  );
};
