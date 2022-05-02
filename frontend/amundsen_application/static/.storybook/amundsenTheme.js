import { create } from '@storybook/theming/create';

export default create({
  base: 'light',

  colorPrimary: '#007DFB', // revlightblue
  colorSecondary: '#0666EB', // revblue

  // UI
  appBg: '#fcfcff', // gray0
  appContentBg: '#DEE2E7', // revgrey2
  appBorderColor: '#4E5867', // revgrey6
  appBorderRadius: 4,

  // Typography
  fontBase: '"Open Sans", sans-serif',
  fontCode: '"Menlo-Bold", monospace',

  // Text colors
  textColor: '#21262E', // revblack
  textInverseColor: '#fcfcff', // gray0

  // Toolbar default and active colors
  barTextColor: '#6DCFFC', // revskyblue2
  barSelectedColor: '#21262E', // revblack
  barBg: '#0666EB', // revblue

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
