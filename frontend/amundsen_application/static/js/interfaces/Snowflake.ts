export interface SnowflakeListing {
  global_name: string;
  name: string;
  title: string;
  subtitle: string; 
  description: string;
}

export interface SnowflakeTableShare {
  owner_account: string;
  name: string;
  listing?: SnowflakeListing
}

export interface SnowflakeTableShares {
  tableUri?: string;
  snowflake_table_shares: SnowflakeTableShare[];
}

export interface SnowflakeTableSharesParams {
  tableUri: string;
}

export interface SnowflakeListingStatsQueryParams {
  listing_global_name: string;
}
