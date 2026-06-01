function addRelToken(link, token) {
  const values = new Set(
    (link.getAttribute('rel') || '').split(/\s+/).filter(Boolean)
  );

  values.add(token);
  link.setAttribute('rel', [...values].join(' '));
}

function getUrl(link) {
  try {
    return new URL(link.getAttribute('href'), window.location.href);
  } catch {
    return null;
  }
}

export function openExtLinksInNewTab() {
  document.querySelectorAll('a[href]').forEach((link) => {
    const url = getUrl(link);

    if (!url) {
      return;
    }

    if (!['http:', 'https:'].includes(url.protocol)) {
      return;
    }

    if (url.origin === window.location.origin) {
      return;
    }

    link.setAttribute('target', '_blank');
    addRelToken(link, 'noopener');
    addRelToken(link, 'noreferrer');
  });
}
