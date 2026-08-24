import { useEffect, useRef, useState } from "react";

interface ShareButtonProps {
  token: string;
  label?: string;
}

// HU-20 (FR-005, D-06): sharing is two interactions - press, see confirmation.
// When the browser blocks the Clipboard API (HTTP origins, denied permission)
// we fall back to a hidden textarea + execCommand, and as a last resort show
// the full link so the user can copy it by hand. The user never sees a raw
// error: a broken clipboard must not read as a broken app.
export function ShareButton({ token, label = "Compartir" }: ShareButtonProps) {
  const [copied, setCopied] = useState(false);
  const [manualLink, setManualLink] = useState<string | null>(null);
  const timer = useRef<number | undefined>(undefined);

  useEffect(() => () => window.clearTimeout(timer.current), []);

  const link = `${window.location.origin}/proyecto/${encodeURIComponent(token)}`;

  async function share() {
    const ok = await copyToClipboard(link);
    if (ok) {
      setManualLink(null);
      setCopied(true);
      window.clearTimeout(timer.current);
      timer.current = window.setTimeout(() => setCopied(false), 2000);
    } else {
      // Visible fallback: the whole link, preselected for a manual copy.
      setManualLink(link);
    }
  }

  return (
    <div className="share">
      <button type="button" className="share__button" onClick={() => void share()}>
        {copied ? "¡Enlace copiado!" : label}
      </button>
      {manualLink && (
        <input
          className="share__fallback"
          type="text"
          readOnly
          value={manualLink}
          onFocus={(event) => event.currentTarget.select()}
          aria-label="Enlace para copiar manualmente"
        />
      )}
    </div>
  );
}

async function copyToClipboard(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch {
    // Fall through to the legacy path below.
  }

  try {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.select();
    const ok = document.execCommand("copy");
    document.body.removeChild(textarea);
    return ok;
  } catch {
    return false;
  }
}
