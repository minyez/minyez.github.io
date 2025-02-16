import { basic, initSidebar, initTopbar } from './modules/layouts';
import {
  loadImg,
  imgPopup,
  initClipboard,
  initToc,
  loadMermaid
} from './modules/components';

loadImg();
initToc();
imgPopup();
initSidebar();
initTopbar();
initClipboard();
loadMermaid();
basic();
