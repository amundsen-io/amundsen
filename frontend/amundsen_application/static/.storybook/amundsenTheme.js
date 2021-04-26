import { create } from '@storybook/theming/create';

export default create({
  base: 'light',

  colorPrimary: '#9c9bff', // indigo30
  colorSecondary: '#665aff', // indigo60

  // UI
  appBg: '#fcfcff', // gray0
  appContentBg: '#cacad9', // gray20
  appBorderColor: '#63637b', // gray60
  appBorderRadius: 4,

  // Typography
  fontBase: '"Open Sans", sans-serif',
  fontCode: '"Menlo-Bold", monospace',

  // Text colors
  textColor: '#292936', // gray100
  textInverseColor: '#fcfcff', // gray0

  // Toolbar default and active colors
  barTextColor: '#dcdcff', // indigo10
  barSelectedColor: '#292936', // gray100
  barBg: '#665aff', // indigo60

  // Form colors
  inputBg: 'white',
  inputBorder: 'silver',
  inputTextColor: 'black',
  inputBorderRadius: 4,

  brandTitle: "Amundsen's Storybook",
  brandUrl: 'https://amundsen.lyft.net/',
  brandImage:
    'https://raw.githubusercontent.com/lyft/amundsen/master/docs/img/logos/amundsen_logo_on_light.svg?sanitize=true',
});
