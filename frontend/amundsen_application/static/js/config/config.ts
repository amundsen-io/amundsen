import { AppConfig, AppConfigExternal } from './config-types';
import configDefault from './config-default';
import configCustom from './config-custom';

// This is not a shallow merge. In two steps we are overriding the application  config
//  Step 1: Any defined members of customConfig will override configDefault.
//  Step 2: Any defined members of configExternal will override the configDefault and configCustom.

const appConfig: AppConfig = {
  ...configDefault,
  ...configCustom,
  ...(((globalThis as unknown) as AppConfigExternal)?.configExternal || {}),
};

export default appConfig;
