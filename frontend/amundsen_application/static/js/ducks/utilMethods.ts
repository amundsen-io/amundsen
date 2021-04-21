import { Tag } from 'interfaces';
import { ActionLogParams, postActionLog } from './log/api/v0';

export function sortTagsAlphabetical(a: Tag, b: Tag): number {
  return a.tag_name.localeCompare(b.tag_name);
}

export function extractFromObj(
  initialObj: object,
  desiredKeys: string[]
): object {
  return Object.keys(initialObj)
    .filter((key) => desiredKeys.indexOf(key) > -1)
    .reduce((obj, key) => {
      obj[key] = initialObj[key];
      return obj;
    }, {});
}

export function filterFromObj(
  initialObj: object,
  rejectedKeys: string[]
): object {
  return Object.keys(initialObj)
    .filter((key) => rejectedKeys.indexOf(key) === -1)
    .reduce((obj, key) => {
      obj[key] = initialObj[key];
      return obj;
    }, {});
}

export function logAction(declaredProps: ActionLogParams) {
  const inferredProps = {
    location: window.location.pathname,
  };

  postActionLog({ ...inferredProps, ...declaredProps });
}

export function logClick(
  event: React.MouseEvent<HTMLElement>,
  declaredProps?: ActionLogParams
) {
  const target = event.currentTarget;
  const inferredProps: ActionLogParams = {
    command: 'click',
    target_id:
      target.dataset && target.dataset.type ? target.dataset.type : target.id,
    label: target.innerText || target.textContent || '',
  };

  if (target.nodeValue !== null) {
    inferredProps.value = target.nodeValue;
  }

  let nodeName = target.nodeName.toLowerCase();
  if (nodeName === 'a') {
    if (target.classList.contains('btn')) {
      nodeName = 'button';
    } else {
      nodeName = 'link';
    }
  }
  inferredProps.target_type = nodeName;

  logAction({ ...inferredProps, ...declaredProps });
}
