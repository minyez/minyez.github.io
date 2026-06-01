import { back2top, loadTooltip, modeWatcher, openExtLinksInNewTab } from '../components';

export function basic() {
  modeWatcher();
  back2top();
  loadTooltip();
  openExtLinksInNewTab();
}
