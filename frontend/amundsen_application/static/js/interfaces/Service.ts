import { Tag } from ".";
import { Attribute } from "./Attribute";

export interface ServiceMetaData {
  key: string;
  name: string;
  description: string;
  criticality?: string;
  last_updated_timestamp?:number;
  owned_by? : string;
  stack? :string;
  tags? : Array<Tag>;
  type? : string
  created_timestamp? : number;
  git_repo? : string;
  victor_ops? :string
  attributes : Array<Attribute>

}
export interface ServiceSource {
  source : string | null;
  source_type : string
}