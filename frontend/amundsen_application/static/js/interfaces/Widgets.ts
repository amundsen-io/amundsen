export interface Widget {
  name: string;
  options: {
    path: string;
    additionalProps?: object;
  };
}
