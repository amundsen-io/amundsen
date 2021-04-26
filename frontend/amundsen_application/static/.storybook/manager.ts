import { addons } from '@storybook/addons';

import amundsenTheme from './amundsenTheme';

addons.setConfig({
  isFullscreen: false,
  showNav: true,
  showPanel: true,
  panelPosition: 'right',
  sidebarAnimations: true,
  enableShortcuts: true,
  isToolshown: true,
  theme: amundsenTheme,
  selectedPanel: undefined,
  initialActive: 'sidebar',
  showRoots: true,
});
